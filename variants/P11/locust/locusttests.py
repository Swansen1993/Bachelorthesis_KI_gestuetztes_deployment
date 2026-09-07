import os
import threading
import time
import uuid
from locust import HttpUser, task, between, events
import boto3
import json

ACTIVE_TARGET = os.getenv("TARGET_METHOD", "pos_086_post_list")


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


class Projekt11Tests(HttpUser):
    wait_time = between(0.1, 0.3)

    def _sign_up(self, email):
        return self.client.post(
            "/api/v1/auth/sign-up",
            json={"email": email, "password": self.password, "name": "Bench User"},
            name="/api/v1/auth/sign-up [seed]",
        )

    def _sign_in(self, email):
        res = self.client.post(
            "/api/v1/auth/sign-in",
            json={"email__eq": email, "password": self.password},
            name="/api/v1/auth/sign-in [seed]",
        )
        if res.status_code == 200:
            return res.json()
        return None

    def on_start(self):
        self.password = "benchmarkPW123!"
        self.email = f"user_{uuid.uuid4().hex[:8]}@test.com"
        self.token = ""
        self.headers = {}
        self.user_token = ""
        self.post_id = 0
        self._sign_up(self.email)
        data = self._sign_in(self.email)
        if data:
            self.token = data["access_token"]
            self.user_token = data["user_info"]["user_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        if ACTIVE_TARGET == "pos_089_post_by_id" and self.token:
            res = self.client.post(
                "/api/v1/post",
                json={
                    "title": "Bench Post",
                    "content": "benchmark body",
                    "tag_ids": [],
                },
                headers=self.headers,
                name="/api/v1/post [seed]",
            )
            if res.status_code == 200:
                self.post_id = res.json().get("id", 0)

    @task(1 if ACTIVE_TARGET == "pos_086_post_list" else 0)
    def pos_086_post_list_test(self):
        self.client.get(
            "/api/v1/post",
            headers=self.headers,
            name="/api/v1/post [GET list]",
        )

    @task(1 if ACTIVE_TARGET == "pos_087_tag_create" else 0)
    def pos_087_tag_create_test(self):
        if not self.token:
            return
        self.client.post(
            "/api/v1/tag",
            json={"name": f"tag_{uuid.uuid4().hex[:8]}", "user_token": self.user_token},
            headers=self.headers,
            name="/api/v1/tag [POST create]",
        )

    @task(1 if ACTIVE_TARGET == "pos_088_sign_in" else 0)
    def pos_088_sign_in_test(self):
        self.client.post(
            "/api/v1/auth/sign-in",
            json={"email__eq": self.email, "password": self.password},
            name="/api/v1/auth/sign-in [POST]",
        )

    @task(1 if ACTIVE_TARGET == "pos_089_post_by_id" else 0)
    def pos_089_post_by_id_test(self):
        if not self.post_id:
            return
        self.client.get(
            f"/api/v1/post/{self.post_id}",
            headers=self.headers,
            name="/api/v1/post/:id [GET by id]",
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
