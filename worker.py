import redis
import time
import os

REDIS_HOST = os.getenv('REDIS_HOST', '172.31.38.213')
r = redis.Redis(host=REDIS_HOST, port=6379, db=0)

print("👷 Worker가 일을 시작합니다...")
while True:
    # Redis에서 작업 꺼내기 (BRPOP: 데이터 올 때까지 대기)
    task = r.brpop('task_queue')
    if task:
        print(f"🔥 작업 처리 중: {task[1].decode('utf-8')}")
        time.sleep(2) # 무거운 작업인 척!