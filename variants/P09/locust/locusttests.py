import os
import threading
import time
import uuid
from locust import HttpUser, task, between, events
import boto3
import json

ACTIVE_TARGET = os.getenv("TARGET_METHOD", "pos_068_user_crud")
SUPERUSER_EMAIL = os.getenv("FIRST_USER_EMAIL", "bench_admin@test.com")
SUPERUSER_PASSWORD = os.getenv("FIRST_USER_PASSWORD", "bench-admin-pass-123")


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


class Projekt09Tests(HttpUser):
    wait_time = between(0.1, 0.3)

    def _login(self, email, password):
        res = self.client.post(
            "/api/v1/login/",
            data={"username": email, "password": password},
            name="/api/v1/login/ [seed]",
        )
        if res.status_code == 200:
            return res.json().get("access_token")
        return None

    def _headers(self, token):
        return {"Authorization": f"Bearer {token}"}

    def on_start(self):
        self.token = ""
        self.headers = {}
        self.target_user_id = None
        if ACTIVE_TARGET == "pos_072_login":
            return
        token = self._login(SUPERUSER_EMAIL, SUPERUSER_PASSWORD)
        if token:
            self.token = token
            self.headers = self._headers(token)
        if ACTIVE_TARGET == "pos_073_users_controller" and self.headers:
            res = self.client.post(
                "/api/v1/users/",
                json={
                    "email": f"target_{uuid.uuid4().hex[:8]}@test.com",
                    "password": "pass1234",
                },
                headers=self.headers,
                name="/api/v1/users/ [seed target]",
            )
            if res.status_code == 200:
                self.target_user_id = res.json().get("id")

    @task(1 if ACTIVE_TARGET == "pos_068_user_crud" else 0)
    def pos_068_user_crud_test(self):
        if not self.headers:
            return
        self.client.get(
            "/api/v1/users/",
            headers=self.headers,
            name="/api/v1/users/ [GET list]",
        )

    @task(1 if ACTIVE_TARGET == "pos_069_crud_base_create" else 0)
    def pos_069_crud_base_create_test(self):
        if not self.headers:
            return
        self.client.post(
            "/api/v1/users/",
            json={
                "email": f"user_{uuid.uuid4().hex[:8]}@test.com",
                "password": "pass1234",
            },
            headers=self.headers,
            name="/api/v1/users/ [POST create]",
        )

    @task(1 if ACTIVE_TARGET == "pos_072_login" else 0)
    def pos_072_login_test(self):
        self.client.post(
            "/api/v1/login/",
            data={"username": SUPERUSER_EMAIL, "password": SUPERUSER_PASSWORD},
            name="/api/v1/login/ [POST]",
        )

    @task(1 if ACTIVE_TARGET == "pos_073_users_controller" else 0)
    def pos_073_users_controller_test(self):
        if not self.headers or not self.target_user_id:
            return
        self.client.get(
            f"/api/v1/users/{self.target_user_id}/",
            headers=self.headers,
            name="/api/v1/users/:id/ [GET]",
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
