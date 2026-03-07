from flask import Flask, request, jsonify
import redis
import os

app = Flask(__name__)
REDIS_HOST = os.getenv('REDIS_HOST', '172.31.38.213') # 5번 서버 사설 IP
r = redis.Redis(host=REDIS_HOST, port=6379, db=0)

@app.route('/')
def index():
    # 브라우저로 접속했을 때 보여줄 화면
    return f"Hello! This is [web1] server. 🚀"

@app.route('/job', methods=['POST'])
def create_job():
    # 작업 요청은 여기서!
    data = request.json
    r.lpush('task_queue', data['task_name'])
    return jsonify({"msg": "작업이 큐에 쌓였습니다!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)