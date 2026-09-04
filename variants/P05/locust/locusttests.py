import os
import threading
import time
import uuid
from locust import HttpUser, task, between, events
import boto3
import json

ACTIVE_TARGET = os.getenv("TARGET_METHOD", "pos_035_list_users")
ADMIN_USERNAME = os.getenv("SEED_ADMIN_USERNAME", "bench_admin")
ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "bench-admin-pass-123")


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


class Projekt05Tests(HttpUser):
    wait_time = between(0.1, 0.3)

    def _log_in(self):
        return self.client.post(
            "/api/v1/account/login/",
            json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
            name="/api/v1/account/login/ [seed]",
        )

    def _create_target_user(self):
        username = f"target_{uuid.uuid4().hex[:8]}"
        res = self.client.post(
            "/api/v1/users/",
            json={
                "username": username,
                "password": ADMIN_PASSWORD,
                "role": "user",
            },
            name="/api/v1/users/ [seed target]",
        )
        if res.status_code == 201:
            self.target_user_id = res.json().get("id")

    def _request_create_user(self):
        self.client.post(
            "/api/v1/users/",
            json={
                "username": f"user_{uuid.uuid4().hex[:8]}",
                "password": ADMIN_PASSWORD,
                "role": "user",
            },
            name="/api/v1/users/ [POST create]",
        )

    def _request_list_users(self):
        self.client.get(
            "/api/v1/users/",
            name="/api/v1/users/ [GET list]",
        )

    def on_start(self):
        self.target_user_id = None
        self.authenticated = False
        if ACTIVE_TARGET == "pos_045_log_in":
            return
        login = self._log_in()
        self.authenticated = login.status_code == 204
        if not self.authenticated:
            return
        if ACTIVE_TARGET in ("pos_040_activate_user", "pos_041_set_user_password"):
            self._create_target_user()

    @task(1 if ACTIVE_TARGET == "pos_035_list_users" else 0)
    def pos_035_list_users_test(self):
        if not self.authenticated:
            return
        self._request_list_users()

    @task(1 if ACTIVE_TARGET == "pos_036_user_tx_storage" else 0)
    def pos_036_user_tx_storage_test(self):
        if not self.authenticated:
            return
        self._request_create_user()

    @task(1 if ACTIVE_TARGET == "pos_037_transaction_manager" else 0)
    def pos_037_transaction_manager_test(self):
        if not self.authenticated:
            return
        self._request_create_user()

    @task(1 if ACTIVE_TARGET == "pos_038_flusher" else 0)
    def pos_038_flusher_test(self):
        if not self.authenticated:
            return
        self._request_create_user()

    @task(1 if ACTIVE_TARGET == "pos_039_create_user" else 0)
    def pos_039_create_user_test(self):
        if not self.authenticated:
            return
        self._request_create_user()

    @task(1 if ACTIVE_TARGET == "pos_040_activate_user" else 0)
    def pos_040_activate_user_test(self):
        if not self.authenticated or not self.target_user_id:
            return
        self.client.delete(
            f"/api/v1/users/{self.target_user_id}/activation/",
            name="/api/v1/users/:id/activation/ [DELETE]",
        )
        self.client.put(
            f"/api/v1/users/{self.target_user_id}/activation/",
            name="/api/v1/users/:id/activation/ [PUT]",
        )

    @task(1 if ACTIVE_TARGET == "pos_041_set_user_password" else 0)
    def pos_041_set_user_password_test(self):
        if not self.authenticated or not self.target_user_id:
            return
        self.client.put(
            f"/api/v1/users/{self.target_user_id}/password/",
            json={"password": f"newpass-{uuid.uuid4().hex[:8]}"},
            name="/api/v1/users/:id/password/ [PUT]",
        )

    @task(1 if ACTIVE_TARGET == "pos_042_list_users" else 0)
    def pos_042_list_users_test(self):
        if not self.authenticated:
            return
        self._request_list_users()

    @task(1 if ACTIVE_TARGET == "pos_043_create_user" else 0)
    def pos_043_create_user_test(self):
        if not self.authenticated:
            return
        self._request_create_user()

    @task(1 if ACTIVE_TARGET == "pos_044_list_users" else 0)
    def pos_044_list_users_test(self):
        if not self.authenticated:
            return
        self._request_list_users()

    @task(1 if ACTIVE_TARGET == "pos_045_log_in" else 0)
    def pos_045_log_in_test(self):
        self.client.post(
            "/api/v1/account/login/",
            json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
            name="/api/v1/account/login/ [log_in]",
        )
        self.client.delete(
            "/api/v1/account/logout/",
            name="/api/v1/account/logout/ [log_out]",
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
