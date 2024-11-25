# Finnhub Streaming Data Pipeline Project

This project is to design pipeline and demonstrate how to run Docker API to fetch stock data of 4 BIGTECH including Facebook, Apple, Amazon, Google and save it for analysis.

![image](https://github.com/user-attachments/assets/b3923007-74ef-4594-b39e-fe76cdc10386)

## Setup Instructions

### Prerequisites

1. Installed Ubutu on VM Vitualbox
2. BigData tools includes: Hadoop, Kafka, Cassandra, Spark, Superset, Kubernetes, Presto installe on your system
3. Docker installed on your system
4. Access to Docker Hub to pull the prebuilt image

## Instructions for running the project
### 1. Clone project on github: 
    git clone https://github.com/heellworld/finnhub_pipeline.git
### 2. Launch components
   #### Zookeeper và Kafka:
   ```bash
	sudo systemctl start zookeeper
    sudo systemctl start kafka
   ```
   #### Hadoop:
   ```bash
	start-dfs.sh
    start-yarn.sh
    hadoop namenode -format
    start-all.sh
   ```
   #### Cassandra:
   ```bash
	sudo systemctl start cassandra
    nodetool status
    ```
   #### Minikube:
   ```bash
   minikube start
   minikube status
   kubectl cluster-info
   ```
   #### Superset:
   ```bash
   source supersetenv/bin/activate
   superset run -p 8099 --with-threads --reload --debugger
   ```
### 4. Start Kubernetes
   ```bash
   kubectl get pods
   kubectl get deployments
   kubectl get services
   ```
### 5. Connect Cassandra to Presto
   #### nano cassandra.properties
   ```bash
    connector.name=cassandra
    cassandra.contact-points=127.0.0.1
   ```
   #### Connect
   ```bash
   cd presto-server-0.289
   su root (login root)
   bin/launcher start
   bin/presto --server 127.0.0.1:8090 --catalog cassandra
   ```
### 6. Connect Presto to Superset
   ```bash
   presto://localhost:8090/cassandra
   ```
## Run Project
### 1. Monitor the data scraping process from Finnhub
   ```bash
   kafka-console-consumer.sh --topic finnhub_data --from-beginning --bootstrap-server localhost:9092
   ```
### 2. Run kafka_prodecer.py to get data from the FinnhubAPI through Producer
### 3. Run Spark Streaming to processing data into Cassandra
   ```bash
   spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,com.datastax.spark:spark-cassandra-connector_2.12:3.5.1 processing_data.py
   ```

## Steps to Run the API

### 1. Pull the Docker Image

Pull the prebuilt Docker image from Docker Hub using the following command:

```bash
docker pull heellworld/finnhub-api:latest
```

### 2. Run the Docker Container

Start the API container using the command:

```bash
docker run -d -p 5000:5000 --name finnhub-api heellworld/finnhub-api:latest
```

### 3. Verify Docker

Check if the container is running:

```bash
docker ps
```

## API Documentation

The API provides two endpoints for retrieving stock data:

### 1. Get Data by Symbol

Retrieves stock data for a specific symbol with a limit on the number of records.

```
GET /api/data/<symbol>
```

#### Parameters:
- `symbol` (path parameter): Stock symbol (e.g., AAPL, GOOGL)
- `limit` (query parameter, optional): Number of records to return (default: 10)

#### Example Request:
```bash
curl http://127.0.0.1:5000/api/data/AAPL?limit=5
```

#### Sample Response:
```json
[
    {
        "symbol": "AAPL",
        "company": "Apple Inc",
        "trade_time": "2024-03-15T10:30:00Z",
        "open_price": 172.5,
        "close_price": 173.2,
        "high_price": 173.8,
        "low_price": 172.3,
        "avg_price": 173.1,
        "total_volume": 1500000,
        "vwap": 173.2
    },
    ...
]
```

### 2. Get Data by Date Range

Retrieves stock data for a specific symbol within a date range.

```
GET /api/data
```

#### Parameters:
- `symbol` (query parameter): Stock symbol (e.g., AAPL, GOOGL)
- `start_date` (query parameter): Start date in YYYY-MM-DD format
- `end_date` (query parameter): End date in YYYY-MM-DD format

#### Example Request:
```bash
curl http://127.0.0.1:5000/api/data?symbol=AAPL&start_date=2024-03-01&end_date=2024-03-15
```

#### Sample Response:
```json
[
    {
        "symbol": "AAPL",
        "company": "Apple Inc",
        "trade_time": "2024-03-15T10:30:00Z",
        "open_price": 172.5,
        "close_price": 173.2,
        "high_price": 173.8,
        "low_price": 172.3,
        "avg_price": 173.1,
        "total_volume": 1500000,
        "vwap": 173.2
    },
    ...
]
```

### Error Responses

The API may return the following error responses:

- `400 Bad Request`: Missing required parameters
- `500 Internal Server Error`: Server-side errors

Error response format:
```json
{
    "error": "Error message description"
}
```

## Data Structure

The API stores stock data with the following schema:

| Column Name  | Data Type  | Description                                    |
|-------------|------------|------------------------------------------------|
| symbol      | text       | Stock symbol (e.g., AAPL, GOOGL)              |
| company     | text       | Company name                                   |
| trade_time  | timestamp  | Time of the trade                             |
| open_price  | double     | Opening price of the trading period           |
| close_price | double     | Closing price of the trading period           |
| high_price  | double     | Highest price during the trading period       |
| low_price   | double     | Lowest price during the trading period        |
| avg_price   | double     | Average price during the trading period       |
| total_volume| int        | Total number of shares traded                 |
| vwap        | double     | Volume Weighted Average Price                 |

**Primary Key**: (symbol, trade_time)

### Notes:
- The `symbol` and `trade_time` combination ensures unique records for each stock at any given time
- VWAP (Volume Weighted Average Price) is calculated based on both price and volume data
- All price fields are stored as double precision floating-point numbers
- Timestamps are stored in UTC timezone

## Stopping the Container

```bash
docker stop finnhub-api
docker rm finnhub-api
```
