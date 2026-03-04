import os
import redis
import pymysql
import json
import time

# 설정 로드
redis_host = os.environ.get("REDIS_HOST", "localhost")
db_host = os.environ.get("DB_HOST", "localhost")

# Redis 및 DB 연결
rd = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)

def get_db_connection():
    return pymysql.connect(
        host=db_host, user='root', password='root_password',
        db='my_login_db', charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

print("🚀 DB 기록 일꾼(Worker)이 가동되었습니다. 큐를 감시합니다...")

while True:
    # 큐에서 작업 가져오기 (데이터가 들어올 때까지 대기)
    job = rd.brpop('login_queue', timeout=5)
    
    if job:
        _, data = job
        task = json.loads(data)
        
        # 실제로 MySQL에 기록 (무거운 작업 수행)
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("CREATE TABLE IF NOT EXISTS login_logs (id INT AUTO_INCREMENT PRIMARY KEY, user_name VARCHAR(50), login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
                cursor.execute("INSERT INTO login_logs (user_name) VALUES (%s)", (task['user_name'],))
            conn.commit()
            print(f"✅ [처리완료] {task['user_name']}님의 로그를 DB에 저장했습니다.")
        finally:
            conn.close()