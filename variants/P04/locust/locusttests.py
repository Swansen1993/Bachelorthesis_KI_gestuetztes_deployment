import os
import threading
import time
import uuid
from locust import HttpUser, task, between, events, stats
import boto3
import json

ACTIVE_TARGET = os.getenv("TARGET_METHOD", "pos_029_create_user")


def _cpu_sampler_loop():
    prev_times = os.times()
    prev_wall = time.monotonic()
    while True:
        time.sleep(10)
        cur_times = os.times()
        cur_wall = time.monotonic()
        wall = cur_wall - prev_wall
        cpu = (cur_times.user - prev_times.user) + (
            cur_times.system - prev_times.system
        )
        prev_times = cur_times
        prev_wall = cur_wall
        pct = (cpu / wall) * 100 if wall else 0
        print(f"RUNNER_CPU {pct:.1f}%", flush=True)


@events.init.add_listener
def _start_cpu_sampler(environment, **kwargs):
    threading.Thread(target=_cpu_sampler_loop, daemon=True).start()


class Projekt04Tests(HttpUser):
    wait_time = between(0.1, 0.3)

    def _register(self, username, password):
        return self.client.post(
            "/user/register",
            json={"username": username, "password": password},
            name="/user/register [POST setup]",
        )

    def _login(self, username, password):
        return self.client.post(
            "/auth/login",
            data={"username": username, "password": password},
            name="/auth/login [POST setup]",
        )

    def on_start(self):
        self.username = f"user_{uuid.uuid4().hex[:8]}"
        self.password = "benchmarkPW123!"
        self.token = ""
        self.headers = {}
        reg = self._register(self.username, self.password)
        if reg.status_code in [200, 201]:
            login = self._login(self.username, self.password)
            if login.status_code == 200:
                self.token = login.json().get("access_token", "")
                self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(1 if ACTIVE_TARGET == "pos_029_create_user" else 0)
    def create_user_029(self):
        self.client.post(
            "/user/register",
            json={
                "username": f"reg_{uuid.uuid4().hex[:8]}",
                "password": "benchmarkPW123!",
            },
            name="/user/register [POST pos_029_create_user]",
        )

    @task(1 if ACTIVE_TARGET == "pos_030_create_user" else 0)
    def create_user_030(self):
        self.client.post(
            "/user/register",
            json={
                "username": f"reg_{uuid.uuid4().hex[:8]}",
                "password": "benchmarkPW123!",
            },
            name="/user/register [POST pos_030_create_user]",
        )

    @task(1 if ACTIVE_TARGET == "pos_031_login" else 0)
    def login_031(self):
        self.client.post(
            "/auth/login",
            data={"username": self.username, "password": self.password},
            name="/auth/login [POST pos_031_login]",
        )

    @task(1 if ACTIVE_TARGET == "pos_032_login" else 0)
    def login_032(self):
        self.client.post(
            "/auth/login",
            data={"username": self.username, "password": self.password},
            name="/auth/login [POST pos_032_login]",
        )

    @task(1 if ACTIVE_TARGET == "pos_033_register" else 0)
    def register_033(self):
        self.client.post(
            "/user/register",
            json={
                "username": f"reg_{uuid.uuid4().hex[:8]}",
                "password": "benchmarkPW123!",
            },
            name="/user/register [POST pos_033_register]",
        )

    @task(1 if ACTIVE_TARGET == "pos_034_create_post" else 0)
    def create_post_034(self):
        if not self.headers:
            return
        self.client.post(
            "/posts/create",
            json={"text": f"Benchmark post {uuid.uuid4().hex[:8]}"},
            headers=self.headers,
            name="/posts/create [POST pos_034_create_post]",
        )


@events.test_stop.add_listener
def send_KPI_To_Aws_S3_Bucket(environment, **kwargs):

    bucket = os.getenv("METRICS_S3_BUCKET")
    s3_path = os.getenv("S3_METRICS_PATH")

    if not bucket or not s3_path:
        return

    total = environment.runner.stats.total

    metrics_payload = {
        "target_method": ACTIVE_TARGET,
        "p95_latency_ms": round(total.get_response_time_percentile(0.95), 2),
        "avg_latency_ms": round(total.avg_response_time, 2),
        "requests_per_sec": round(total.total_rps, 2),
        "error_rate_percent": round(total.fail_ratio * 100, 2),
        "total_requests": total.num_requests,
        "total_failures": total.num_failures,
    }

    s3_client = boto3.client("s3", region_name="eu-central-1")
    print("DEBUG bucket:", bucket)
    print("DEBUG s3_path:", s3_path)
    print("DEBUG target:", ACTIVE_TARGET)
    s3_client.put_object(
        Bucket=bucket,
        Key=s3_path,
        Body=json.dumps(metrics_payload, indent=2),
        ContentType="application/json",
    )
