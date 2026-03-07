FROM python:3.9-slim

WORKDIR /app

# 라이브러리 먼저 설치 (캐싱 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

EXPOSE 5000
CMD ["python", "app.py"]