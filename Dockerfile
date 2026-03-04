# 1. 파이썬 3.13 버전이 설치된 가벼운 리눅스를 베이스로 사용합니다.
FROM python:3.13-slim

# 2. 컨테이너 안에서 작업할 폴더를 만듭니다.
WORKDIR /app

# 3. 필요한 라이브러리 목록 파일을 복사하고 설치합니다.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 현재 폴더의 모든 코드(app.py 등)를 컨테이너 안으로 복사합니다.
COPY . .

# 5. 이 컨테이너는 5000번 포트를 사용할 예정이라고 알려줍니다.
EXPOSE 5000

# 6. 컨테이너가 시작될 때 서버를 실행하는 명령어입니다.
CMD ["python", "app.py"]