from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    from_json, col, expr, first, last, max, min, 
    avg, sum, window, from_unixtime, current_timestamp
)
from datetime import datetime
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, LongType, ArrayType
import logging
import os
from datetime import datetime

# Cấu hình checkpoint directory
current_dir = os.path.dirname(os.path.abspath(__file__))
base_checkpoint_dir = os.path.join(current_dir, "checkpoints")
job_name = "kafka_to_cassandra"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
checkpoint_dir = os.path.join(base_checkpoint_dir, job_name, timestamp)

# Đảm bảo thư mục tồn tại

os.makedirs(checkpoint_dir, exist_ok=True)


# Logging configuration
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Kafka Configuration
KAFKA_HOST = 'localhost'
KAFKA_PORT = 9092
KAFKA_TOPIC = 'finnhub_data'

# Cassandra Configuration
CASSANDRA_HOST = 'localhost'
CASSANDRA_PORT = 9042
CASSANDRA_KEYSPACE = 'finnhub_data'
CASSANDRA_TABLE = 'raw_trade_data'

# Định nghĩa schema cho dữ liệu Kafka
json_schema = StructType([
    StructField("type", StringType(), True),
    StructField("data", ArrayType(StructType([
        StructField("c", ArrayType(StringType()), True),
        StructField("p", DoubleType(), True), 
        StructField("s", StringType(), True),
        StructField("t", LongType(), True),
        StructField("v", IntegerType(), True),
        StructField("company", StringType(), True)
    ])), True)
])


# Tạo Spark Session
spark = SparkSession.builder \
    .appName("Spark: Kafka to Cassandra Real-time Processing") \
    .config("spark.sql.streaming.checkpointLocation", checkpoint_dir) \
    .config("spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,"
            "com.datastax.spark:spark-cassandra-connector_2.12:3.5.1") \
    .config("spark.cassandra.connection.host", CASSANDRA_HOST) \
    .config("spark.cassandra.connection.port", CASSANDRA_PORT) \
    .config('spark.cassandra.output.consistency.level', 'ONE') \
    .config("spark.sql.shuffle.partitions", 4) \
    .master('local[*]') \
    .getOrCreate()


# Tiến hành ReadStream từ Kafka_Topic sau đó xử lý consume bằng spark sql
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", f"{KAFKA_HOST}:{KAFKA_PORT}") \
    .option("failOnDataLoss", "false") \
    .option("subscribe", f"{KAFKA_TOPIC}") \
    .option("startingOffsets", "earliest") \
    .load()

json_df = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING) as msg_value")

# Đầu tiên, explode data array để xử lý từng record
json_expanded_df = json_df.withColumn("msg_value", from_json(json_df["msg_value"], json_schema)) \
    .select("msg_value.*") \
    .select("type", "data") \
    .selectExpr("explode(data) as data")

# Sau đó mới select các trường cụ thể
exploded_df = json_expanded_df.select(
                                from_unixtime(col("data.t") / 1000).cast("timestamp").alias("trade_time"),
                                col("data.s").alias("symbol"),
                                col("data.company").alias("company"),
                                col("data.p").alias("price"),
                                col("data.v").alias("volume")
                            ) 
df_with_date = exploded_df.withColumn("current_time", current_timestamp())


# Xử lý dữ liệu để đưa vào Cassandra với dữ liệu Cassandra đã tạo như sau:
'''
CREATE TABLE IF NOT EXISTS finnhub_data.raw_trade_data (
    symbol text,
    company text,
    trade_time timestamp,
    open_price double,
    close_price double,
    high_price double,
    low_price double,
    avg_price double,
    total_volume int,
    vwap double,
    PRIMARY KEY ((symbol), trade_time)
) WITH CLUSTERING ORDER BY (trade_time DESC);
'''

processed_df = df_with_date \
    .withWatermark("trade_time", "5 seconds") \
    .groupBy(
        "symbol",
        "company",
        window("trade_time", "5 seconds")
    ) \
    .agg(
        first("price").alias("open_price"),
        last("price").alias("close_price"),
        max("price").alias("high_price"),
        min("price").alias("low_price"),
        avg("price").alias("avg_price"),
        sum("volume").cast(IntegerType()).alias("total_volume"),
        expr("sum(price * volume) / sum(volume)").alias("vwap")
    ) \
    .select(
        "symbol",
        "company",
        col("window.start").alias("trade_time"),
        "open_price",
        "close_price", 
        "high_price",
        "low_price",
        "avg_price",
        "total_volume",
        "vwap"
    )


# Insert data đã xử lý vào Casssandra 
def foreach_batch_function(df, epoch_id):
    df.write \
        .format("org.apache.spark.sql.cassandra") \
        .mode("append") \
        .option("keyspace", CASSANDRA_KEYSPACE) \
        .option("table", CASSANDRA_TABLE) \
        .option("spark.cassandra.connection.host", CASSANDRA_HOST) \
        .option("spark.cassandra.connection.port", CASSANDRA_PORT) \
        .save()
    print(f"Successfully wrote batch {epoch_id} to Cassandra")

# Write processed data to Cassandra
writing_df = processed_df \
    .writeStream \
    .foreachBatch(foreach_batch_function) \
    .option("checkpointLocation", checkpoint_dir) \
    .trigger(processingTime="5 seconds") \
    .start()

# Wait for the termination
writing_df.awaitTermination()

# Tiến hành run với câu lệnh như sau:
# spark-submit --packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.5.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,com.datastax.spark:spark-cassandra-connector_2.12:3.5.1 processing_data.py





