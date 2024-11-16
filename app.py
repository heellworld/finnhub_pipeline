from flask import Flask, jsonify, request
import requests

# Khởi tạo Flask app
app = Flask(__name__)

# Cấu hình Presto REST API
PRESTO_URL = "http://127.0.0.1:8090/v1/statement"  # Địa chỉ Presto REST API
PRESTO_HEADERS = {
    "X-Presto-User": "flask_user",  # Tên người dùng cho Presto
    "X-Presto-Catalog": "cassandra",
    "X-Presto-Schema": "finnhub_data",
}

# Endpoint: Lấy dữ liệu theo symbol
@app.route('/api/data/<symbol>', methods=['GET'])
def get_data_by_symbol(symbol):
    """
    Lấy dữ liệu từ bảng raw_trade_data theo symbol thông qua Presto.
    """
    try:
        limit = int(request.args.get('limit', 10))  # Số bản ghi (mặc định là 10)

        # Xây dựng câu query SQL
        query = f"SELECT * FROM raw_trade_data WHERE symbol = '{symbol}' LIMIT {limit}"

        # Gửi truy vấn tới Presto
        response = requests.post(PRESTO_URL, headers=PRESTO_HEADERS, data=query)
        response.raise_for_status()
        query_results = response.json()

        # Lấy dữ liệu từ query_results
        data = []
        while 'nextUri' in query_results:
            data.extend(query_results.get('data', []))
            next_uri = query_results['nextUri']
            query_results = requests.get(next_uri, headers=PRESTO_HEADERS).json()

        # Lấy danh sách cột từ kết quả
        columns = [col['name'] for col in query_results.get('columns', [])]

        # Chuyển đổi dữ liệu thành danh sách dict
        data_dicts = [dict(zip(columns, row)) for row in data]
        return jsonify(data_dicts), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    except KeyError as e:
        return jsonify({"error": f"KeyError: {e}"}), 500

# Endpoint: Lấy dữ liệu theo ngày
@app.route('/api/data', methods=['GET'])
def get_data_by_date():
    """
    Lấy dữ liệu từ bảng raw_trade_data theo khoảng thời gian thông qua Presto.
    """
    try:
        symbol = request.args.get('symbol')
        start_date = request.args.get('start_date')  # Format: YYYY-MM-DD
        end_date = request.args.get('end_date')      # Format: YYYY-MM-DD

        # Xác minh input
        if not symbol or not start_date or not end_date:
            return jsonify({"error": "symbol, start_date, and end_date are required"}), 400

        # Xây dựng câu query SQL
        query = f"""
        SELECT * FROM raw_trade_data 
        WHERE symbol = '{symbol}' 
          AND trade_time >= TIMESTAMP '{start_date}' 
          AND trade_time <= TIMESTAMP '{end_date}'
        ORDER BY trade_time DESC
        """

        # Gửi truy vấn tới Presto
        response = requests.post(PRESTO_URL, headers=PRESTO_HEADERS, data=query)
        response.raise_for_status()
        query_results = response.json()

        # Lấy dữ liệu từ query_results
        data = []
        while 'nextUri' in query_results:
            data.extend(query_results.get('data', []))
            next_uri = query_results['nextUri']
            query_results = requests.get(next_uri, headers=PRESTO_HEADERS).json()

        # Lấy danh sách cột từ kết quả
        columns = [col['name'] for col in query_results.get('columns', [])]

        # Chuyển đổi dữ liệu thành danh sách dict
        data_dicts = [dict(zip(columns, row)) for row in data]
        return jsonify(data_dicts), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    except KeyError as e:
        return jsonify({"error": f"KeyError: {e}"}), 500

# Chạy server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
