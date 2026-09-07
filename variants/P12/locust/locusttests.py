import os
import threading
import time
import uuid
from locust import HttpUser, task, between, events
import boto3
import json

ACTIVE_TARGET = os.getenv("TARGET_METHOD", "pos_091_get_user_books")
SEED_EMAIL = os.getenv("SEED_USER_EMAIL", "bench@test.com")
SEED_PASSWORD = os.getenv("SEED_USER_PASSWORD", "bench-pass-123")

SIGNUP_TARGETS = (
    "pos_096_create_url_safe_token",
    "pos_098_create_user",
    "pos_105_signup_ctrl",
)
LOGIN_TARGETS = (
    "pos_092_get_user_by_email",
    "pos_094_create_access_token",
    "pos_106_login_ctrl",
)
BOOK_NEEDED_TARGETS = (
    "pos_099_add_review",
    "pos_100_delete_review",
    "pos_101_add_tags_to_book_svc",
    "pos_104_update_book",
    "pos_107_add_review_ctrl",
    "pos_108_add_tags_to_book_ctrl",
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


class Projekt12Tests(HttpUser):
    wait_time = between(0.1, 0.3)

    def _login(self, email, password):
        res = self.client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
            name="/api/v1/auth/login [seed]",
        )
        if res.status_code == 200:
            return res.json()
        return None

    def _create_book(self):
        res = self.client.post(
            "/api/v1/books/",
            json={
                "title": f"Bench Book {uuid.uuid4().hex[:8]}",
                "author": "Bench Author",
                "publisher": "Bench Publisher",
                "published_date": "2024-01-01",
                "page_count": 200,
                "language": "en",
            },
            headers=self.headers,
            name="/api/v1/books/ [seed]",
        )
        if res.status_code == 201:
            return res.json().get("uid")
        return None

    def on_start(self):
        self.password = "bench-pass-123"
        self.token = ""
        self.headers = {}
        self.user_uid = ""
        self.book_uid = ""
        if ACTIVE_TARGET in SIGNUP_TARGETS:
            return
        data = self._login(SEED_EMAIL, SEED_PASSWORD)
        if data:
            self.token = data["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            self.user_uid = data.get("user", {}).get("uid", "")
        if not self.token:
            return
        if ACTIVE_TARGET in BOOK_NEEDED_TARGETS:
            self.book_uid = self._create_book() or ""

    def _book_payload(self):
        return {
            "title": f"Bench Book {uuid.uuid4().hex[:8]}",
            "author": "Bench Author",
            "publisher": "Bench Publisher",
            "published_date": "2024-01-01",
            "page_count": 200,
            "language": "en",
        }

    def _signup_payload(self):
        short = uuid.uuid4().hex[:6]
        return {
            "first_name": "Bench",
            "last_name": "User",
            "username": f"u{short}",
            "email": f"u{uuid.uuid4().hex[:8]}@test.com",
            "password": self.password,
        }

    @task(1 if ACTIVE_TARGET == "pos_091_get_user_books" else 0)
    def pos_091_get_user_books_test(self):
        if not self.user_uid:
            return
        self.client.get(
            f"/api/v1/books/user/{self.user_uid}",
            headers=self.headers,
            name="/api/v1/books/user/:uid [GET]",
        )

    @task(1 if ACTIVE_TARGET == "pos_092_get_user_by_email" else 0)
    def pos_092_get_user_by_email_test(self):
        self._login(SEED_EMAIL, SEED_PASSWORD)

    @task(1 if ACTIVE_TARGET == "pos_093_get_tags" else 0)
    def pos_093_get_tags_test(self):
        self.client.get(
            "/api/v1/tags/",
            headers=self.headers,
            name="/api/v1/tags/ [GET]",
        )

    @task(1 if ACTIVE_TARGET == "pos_094_create_access_token" else 0)
    def pos_094_create_access_token_test(self):
        self._login(SEED_EMAIL, SEED_PASSWORD)

    @task(1 if ACTIVE_TARGET == "pos_095_decode_token" else 0)
    def pos_095_decode_token_test(self):
        self.client.get(
            "/api/v1/auth/logout",
            headers=self.headers,
            name="/api/v1/auth/logout [GET]",
        )

    @task(1 if ACTIVE_TARGET == "pos_096_create_url_safe_token" else 0)
    def pos_096_create_url_safe_token_test(self):
        self.client.post(
            "/api/v1/auth/signup",
            json=self._signup_payload(),
            name="/api/v1/auth/signup [POST]",
        )

    @task(1 if ACTIVE_TARGET == "pos_097_create_book" else 0)
    def pos_097_create_book_test(self):
        self.client.post(
            "/api/v1/books/",
            json=self._book_payload(),
            headers=self.headers,
            name="/api/v1/books/ [POST service]",
        )

    @task(1 if ACTIVE_TARGET == "pos_098_create_user" else 0)
    def pos_098_create_user_test(self):
        self.client.post(
            "/api/v1/auth/signup",
            json=self._signup_payload(),
            name="/api/v1/auth/signup [POST service]",
        )

    @task(1 if ACTIVE_TARGET == "pos_099_add_review" else 0)
    def pos_099_add_review_test(self):
        if not self.book_uid:
            return
        self.client.post(
            f"/api/v1/reviews/book/{self.book_uid}",
            json={
                "rating": 4,
                "review_text": f"benchmark review {uuid.uuid4().hex[:6]}",
            },
            headers=self.headers,
            name="/api/v1/reviews/book/:uid [POST service]",
        )

    @task(1 if ACTIVE_TARGET == "pos_100_delete_review" else 0)
    def pos_100_delete_review_test(self):
        if not self.book_uid:
            return
        res = self.client.post(
            f"/api/v1/reviews/book/{self.book_uid}",
            json={"rating": 4, "review_text": f"review {uuid.uuid4().hex[:6]}"},
            headers=self.headers,
            name="/api/v1/reviews/book/:uid [POST create-review]",
        )
        if res.status_code in (200, 201):
            review_uid = res.json().get("uid")
            self.client.delete(
                f"/api/v1/reviews/{review_uid}",
                headers=self.headers,
                name="/api/v1/reviews/:uid [DELETE]",
            )

    @task(1 if ACTIVE_TARGET == "pos_101_add_tags_to_book_svc" else 0)
    def pos_101_add_tags_to_book_svc_test(self):
        if not self.book_uid:
            return
        self.client.post(
            f"/api/v1/tags/book/{self.book_uid}/tags",
            json={"tags": [{"name": f"tag_{uuid.uuid4().hex[:8]}"}]},
            headers=self.headers,
            name="/api/v1/tags/book/:uid/tags [POST service]",
        )

    @task(1 if ACTIVE_TARGET == "pos_102_add_tag" else 0)
    def pos_102_add_tag_test(self):
        self.client.post(
            "/api/v1/tags/",
            json={"name": f"tag_{uuid.uuid4().hex[:8]}"},
            headers=self.headers,
            name="/api/v1/tags/ [POST]",
        )

    @task(1 if ACTIVE_TARGET == "pos_103_create_book_ctrl" else 0)
    def pos_103_create_book_ctrl_test(self):
        self.client.post(
            "/api/v1/books/",
            json=self._book_payload(),
            headers=self.headers,
            name="/api/v1/books/ [POST controller]",
        )

    @task(1 if ACTIVE_TARGET == "pos_104_update_book" else 0)
    def pos_104_update_book_test(self):
        if not self.book_uid:
            return
        self.client.patch(
            f"/api/v1/books/{self.book_uid}",
            json={
                "title": f"Updated {uuid.uuid4().hex[:8]}",
                "author": "Bench Author",
                "publisher": "Bench Publisher",
                "page_count": 210,
                "language": "en",
            },
            headers=self.headers,
            name="/api/v1/books/:uid [PATCH]",
        )

    @task(1 if ACTIVE_TARGET == "pos_105_signup_ctrl" else 0)
    def pos_105_signup_ctrl_test(self):
        self.client.post(
            "/api/v1/auth/signup",
            json=self._signup_payload(),
            name="/api/v1/auth/signup [POST controller]",
        )

    @task(1 if ACTIVE_TARGET == "pos_106_login_ctrl" else 0)
    def pos_106_login_ctrl_test(self):
        self._login(SEED_EMAIL, SEED_PASSWORD)

    @task(1 if ACTIVE_TARGET == "pos_107_add_review_ctrl" else 0)
    def pos_107_add_review_ctrl_test(self):
        if not self.book_uid:
            return
        self.client.post(
            f"/api/v1/reviews/book/{self.book_uid}",
            json={
                "rating": 4,
                "review_text": f"benchmark review {uuid.uuid4().hex[:6]}",
            },
            headers=self.headers,
            name="/api/v1/reviews/book/:uid [POST controller]",
        )

    @task(1 if ACTIVE_TARGET == "pos_108_add_tags_to_book_ctrl" else 0)
    def pos_108_add_tags_to_book_ctrl_test(self):
        if not self.book_uid:
            return
        self.client.post(
            f"/api/v1/tags/book/{self.book_uid}/tags",
            json={"tags": [{"name": f"tag_{uuid.uuid4().hex[:8]}"}]},
            headers=self.headers,
            name="/api/v1/tags/book/:uid/tags [POST controller]",
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
