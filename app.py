import os
import uuid
import redis
import json
import time
from flask import Flask, request, make_response

app = Flask(__name__)

# [1] Redis 설정 (세션용 + 메시지 큐용)
redis_host = os.environ.get("REDIS_HOST", "localhost")
rd = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)

@app.route('/')
def home():
    user_ip = request.headers.get('X-Real-IP', request.remote_addr)
    session_id = request.cookies.get('my_session_id')
    
    if session_id and rd.exists(session_id):
        user_name = rd.get(session_id)
        return f"<h1>[CI/CD확인]</h1> 접속 IP: {user_ip}<br>환영합니다, {user_name}님! (현재 메시지 큐 가동 중)"
    
    return "로그인이 필요합니다. <a href='/login'>[여기서 로그인]</a>"

@app.route('/login')
def login():
    session_id = str(uuid.uuid4())
    user_name = "Master_User"
    
    # [A] 기존 로직: 세션 저장은 즉시 처리 (0.001초)
    rd.set(session_id, user_name, ex=3600)
    
    # [B] 변경 로직: 무거운 MySQL 기록은 큐(Redis)에 던지기만 함 (방패 역할)
    # 이제 Flask는 DB 접속이 끝날 때까지 기다리지 않습니다!
    log_data = {
        "user_name": user_name,
        "login_time": time.time()
    }
    rd.lpush('login_queue', json.dumps(log_data))
    
    resp = make_response("로그인 성공! (상세 기록은 메시지 큐에서 처리 중입니다) <a href='/'>메인으로 가기</a>")
    resp.set_cookie('my_session_id', session_id)
    return resp

if __name__ == '__main__':
    port = int(os.environ.get("FLASK_RUN_PORT", 5000))
    app.run(host='0.0.0.0', port=port)