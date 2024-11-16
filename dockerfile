# Sử dụng Python làm base image
FROM python:3.10-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép toàn bộ project vào container
COPY . /app

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Mở cổng để Flask chạy
EXPOSE 5000

# Lệnh khởi chạy ứng dụng Flask
CMD ["python", "app.py"]
