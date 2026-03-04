import os
import uuid
import redis
import pymysql  # MySQL 접속용
from flask import Flask, request, make_response

app = Flask(__name__)

# [1] Redis 설정 (세션용)
redis_host = os.environ.get("REDIS_HOST", "localhost")
rd = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)

# [2] MySQL 설정 (영구 저장용)
db_host = os.environ.get("DB_HOST", "localhost")

def get_db_connection():
    return pymysql.connect(
        host=db_host,
        user='root',
        password='root_password',
        db='my_login_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def home():
    # Nginx가 보낸 진짜 IP 읽어보기 (공부한 내용!)
    user_ip = request.headers.get('X-Real-IP', request.remote_addr)
    session_id = request.cookies.get('my_session_id')
    
    if session_id and rd.exists(session_id):
        user_name = rd.get(session_id)
        return f"<h1>[Main Server]</h1> 접속 IP: {user_ip}<br>환영합니다, {user_name}님! (데이터: Redis+MySQL)"
    
    return "로그인이 필요합니다. <a href='/login'>[여기서 로그인]</a>"

@app.route('/login')
def login():
    session_id = str(uuid.uuid4())
    user_name = "Master_User"
    
    # [3] Redis에 세션 저장 (1시간)
    rd.set(session_id, user_name, ex=3600)
    
    # [4] MySQL에 로그인 기록 남기 (관문 E)
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 테이블이 없으면 만들기 (처음 한 번만)
            cursor.execute("CREATE TABLE IF NOT EXISTS login_logs (id INT AUTO_INCREMENT PRIMARY KEY, user_name VARCHAR(50), login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
            # 로그인 기록 삽입
            cursor.execute("INSERT INTO login_logs (user_name) VALUES (%s)", (user_name,))
        conn.commit()
    finally:
        conn.close()
    
    resp = make_response("로그인 성공 및 DB 기록 완료! <a href='/'>메인으로 가기</a>")
    resp.set_cookie('my_session_id', session_id)
    return resp

if __name__ == '__main__':
    port = int(os.environ.get("FLASK_RUN_PORT", 5000))
    app.run(host='0.0.0.0', port=port)