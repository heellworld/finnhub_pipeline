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

### 4. Test API

To ensure the API is functioning, send an HTTP request, examples:

```bash
curl http://127.0.0.1:5000/api/data/AAPL?limit=5
```

## Data Structure

The API stores stock data with the following schema:

| Column Name  | Data Type  | Description                                    |
|-------------|------------|------------------------------------------------|
| symbol      | text       | Stock symbol (AMZN, AAPL, GOOGL, META)              |
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
