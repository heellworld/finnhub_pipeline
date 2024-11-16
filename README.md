# Finnhub API Docker Project

This project demonstrates how to run a Dockerized API to fetch stock data and save it for analysis.

## Setup Instructions

### Prerequisites

1. Docker installed on your system
2. Access to Docker Hub to pull the prebuilt image

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
