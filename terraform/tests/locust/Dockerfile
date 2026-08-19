FROM python:3.11-slim
WORKDIR /mnt/locust

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 

COPY locusttests.py .

ENTRYPOINT [ "sh", "-c", "exec locust -f locusttests.py --headless --host=${TARGET_URL} -u ${LOCUST_USERS} -r ${LOCUST_SPAWN_RATE} --run-time ${LOCUST_RUN_TIME} --json-file=/mnt/locust/results/stats.json"]