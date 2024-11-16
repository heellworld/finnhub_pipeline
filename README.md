# Finnhub API Docker Project

This project demonstrates how to run a Dockerized API to fetch stock data and save it for analysis.

---

## **Setup Instructions**

### **Prerequisites**
1. Docker installed on your system.
2. Access to Docker Hub to pull the prebuilt image.

---

## **Steps to Run the API**

### **1. Pull the Docker Image**
Pull the prebuilt Docker image from Docker Hub using the following command:
```
docker pull heellworld/finnhub-api:latest
```

### **2. Run the Docker Container**
Start the API container using the command:
```
docker run -d -p 5000:5000 --name finnhub-api heellworld/finnhub-api:latest
```
### **3. Verify Docker**
Check if the container is running:
```
docker ps
```
### **4. Test API**
To ensure the API is functioning, send an HTTP request, examples:
```
curl http://127.0.0.1:5000/api/data/AAPL?limit=5
```
## **Stopping the Container**
```
docker stop finnhub-api
docker rm finnhub-api
```
