import os
import threading
import time
import uuid
from locust import HttpUser, task, between, events
import boto3
import json

ACTIVE_TARGET = os.getenv("TARGET_METHOD", "pos_074_db_setup")

REGISTER_TARGETS = (
    "pos_074_db_setup",
    "pos_075_user_db_create",
    "pos_078_manager_create",
    "pos_082_register_controller",
)
LOGIN_TARGETS = (
    "pos_079_manager_authenticate",
    "pos_085_login_controller",
)
ME_TARGETS = (
    "pos_080_authenticator_me",
    "pos_083_me_controller",
)


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


class Projekt10Tests(HttpUser):
    wait_time = between(0.1, 0.3)

    def _register(self, email):
        res = self.client.post(
            "/auth/register",
            json={"email": email, "password": self.password},
            name="/auth/register [seed]",
        )
        return res.status_code == 201

    def _login(self, email):
        res = self.client.post(
            "/auth/jwt/login",
            data={"username": email, "password": self.password},
            name="/auth/jwt/login [seed]",
        )
        if res.status_code == 200:
            return res.json().get("access_token")
        return None

    def on_start(self):
        self.password = "benchmarkPW123!"
        self.base_email = f"user_{uuid.uuid4().hex[:8]}@test.com"
        self.token = ""
        self.headers = {}
        if ACTIVE_TARGET in LOGIN_TARGETS:
            self._register(self.base_email)
            return
        if ACTIVE_TARGET in ME_TARGETS or ACTIVE_TARGET == "pos_081_backend_logout":
            self._register(self.base_email)
            token = self._login(self.base_email)
            if token:
                self.token = token
                self.headers = {"Authorization": f"Bearer {token}"}
            return
        if ACTIVE_TARGET == "pos_084_forgot_password_controller":
            self._register(self.base_email)

    @task(1 if ACTIVE_TARGET == "pos_074_db_setup" else 0)
    def pos_074_db_setup_test(self):
        email = f"reg_{uuid.uuid4().hex[:8]}@test.com"
        self.client.post(
            "/auth/register",
            json={"email": email, "password": self.password},
            name="/auth/register [POST db-setup]",
        )

    @task(1 if ACTIVE_TARGET == "pos_075_user_db_create" else 0)
    def pos_075_user_db_create_test(self):
        email = f"reg_{uuid.uuid4().hex[:8]}@test.com"
        self.client.post(
            "/auth/register",
            json={"email": email, "password": self.password},
            name="/auth/register [POST user-db-create]",
        )

    @task(1 if ACTIVE_TARGET == "pos_078_manager_create" else 0)
    def pos_078_manager_create_test(self):
        email = f"reg_{uuid.uuid4().hex[:8]}@test.com"
        self.client.post(
            "/auth/register",
            json={"email": email, "password": self.password},
            name="/auth/register [POST manager-create]",
        )

    @task(1 if ACTIVE_TARGET == "pos_079_manager_authenticate" else 0)
    def pos_079_manager_authenticate_test(self):
        self.client.post(
            "/auth/jwt/login",
            data={"username": self.base_email, "password": self.password},
            name="/auth/jwt/login [POST authenticate]",
        )

    @task(1 if ACTIVE_TARGET == "pos_080_authenticator_me" else 0)
    def pos_080_authenticator_me_test(self):
        if not self.token:
            return
        self.client.get(
            "/users/me",
            headers=self.headers,
            name="/users/me [GET authenticator]",
        )

    @task(1 if ACTIVE_TARGET == "pos_081_backend_logout" else 0)
    def pos_081_backend_logout_test(self):
        if not self.token:
            return
        self.client.post(
            "/auth/jwt/logout",
            headers=self.headers,
            name="/auth/jwt/logout [POST]",
        )

    @task(1 if ACTIVE_TARGET == "pos_082_register_controller" else 0)
    def pos_082_register_controller_test(self):
        email = f"reg_{uuid.uuid4().hex[:8]}@test.com"
        self.client.post(
            "/auth/register",
            json={"email": email, "password": self.password},
            name="/auth/register [POST controller]",
        )

    @task(1 if ACTIVE_TARGET == "pos_083_me_controller" else 0)
    def pos_083_me_controller_test(self):
        if not self.token:
            return
        self.client.get(
            "/users/me",
            headers=self.headers,
            name="/users/me [GET controller]",
        )

    @task(1 if ACTIVE_TARGET == "pos_084_forgot_password_controller" else 0)
    def pos_084_forgot_password_controller_test(self):
        self.client.post(
            "/auth/forgot-password",
            json={"email": self.base_email},
            name="/auth/forgot-password [POST]",
        )

    @task(1 if ACTIVE_TARGET == "pos_085_login_controller" else 0)
    def pos_085_login_controller_test(self):
        self.client.post(
            "/auth/jwt/login",
            data={"username": self.base_email, "password": self.password},
            name="/auth/jwt/login [POST controller]",
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
