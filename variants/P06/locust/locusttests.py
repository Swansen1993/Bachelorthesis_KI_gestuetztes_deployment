import os
import threading
import time
import uuid
from locust import HttpUser, task, between, events
import boto3
import json

ACTIVE_TARGET = os.getenv("TARGET_METHOD", "pos_046_list_articles")


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


class Projekt06Tests(HttpUser):
    wait_time = between(0.1, 0.3)

    def _register(self, username, email):
        res = self.client.post(
            "/api/users",
            json={
                "user": {
                    "username": username,
                    "email": email,
                    "password": self.password,
                }
            },
            name="/api/users [POST seed register]",
        )
        if res.status_code == 201:
            return res.json().get("user", {}).get("token")
        return None

    def _create_article(self, headers, title_prefix):
        res = self.client.post(
            "/api/articles",
            json={
                "article": {
                    "title": f"{title_prefix} {uuid.uuid4().hex[:8]}",
                    "description": "Benchmark description",
                    "body": "Benchmark article body text",
                    "tagList": [],
                }
            },
            headers=headers,
            name="/api/articles [POST seed article]",
        )
        if res.status_code == 201:
            return res.json().get("article", {}).get("slug")
        return None

    def _seed_feed_target(self):
        author_name = f"author_{uuid.uuid4().hex[:8]}"
        author_email = f"{author_name}@test.com"
        author_token = self._register(author_name, author_email)
        if not author_token:
            return
        author_headers = {"Authorization": f"Token {author_token}"}
        slug = self._create_article(author_headers, "Feed Article")
        if slug:
            self.client.post(
                f"/api/profiles/{author_name}/follow",
                headers=self.headers,
                name="/api/profiles/:username/follow [seed]",
            )

    def on_start(self):
        self.username = f"user_{uuid.uuid4().hex[:8]}"
        self.email = f"{self.username}@test.com"
        self.password = "benchmarkPW123!"
        self.token = ""
        self.headers = {}
        self.article_slug = ""
        token = self._register(self.username, self.email)
        if token:
            self.token = token
            self.headers = {"Authorization": f"Token {token}"}
        if not self.token:
            return
        if ACTIVE_TARGET == "pos_047_articles_feed":
            self._seed_feed_target()
            return
        if ACTIVE_TARGET in (
            "pos_046_list_articles",
            "pos_048_favorite_article",
            "pos_049_unfavorite_article",
            "pos_052_create_comment",
        ):
            self.article_slug = self._create_article(self.headers, "Seed Article") or ""

    @task(1 if ACTIVE_TARGET == "pos_046_list_articles" else 0)
    def pos_046_list_articles_test(self):
        if not self.token:
            return
        self.client.get(
            f"/api/articles?author={self.username}",
            headers=self.headers,
            name="/api/articles [GET list]",
        )

    @task(1 if ACTIVE_TARGET == "pos_047_articles_feed" else 0)
    def pos_047_articles_feed_test(self):
        if not self.token:
            return
        self.client.get(
            "/api/articles/feed/",
            headers=self.headers,
            name="/api/articles/feed/ [GET]",
        )

    @task(1 if ACTIVE_TARGET == "pos_048_favorite_article" else 0)
    def pos_048_favorite_article_test(self):
        if not self.token or not self.article_slug:
            return
        self.client.post(
            f"/api/articles/{self.article_slug}/favorite",
            headers=self.headers,
            name="/api/articles/:slug/favorite [POST]",
        )

    @task(1 if ACTIVE_TARGET == "pos_049_unfavorite_article" else 0)
    def pos_049_unfavorite_article_test(self):
        if not self.token or not self.article_slug:
            return
        self.client.delete(
            f"/api/articles/{self.article_slug}/favorite",
            headers=self.headers,
            name="/api/articles/:slug/favorite [DELETE]",
        )

    @task(1 if ACTIVE_TARGET == "pos_050_create_article" else 0)
    def pos_050_create_article_test(self):
        if not self.token:
            return
        self.client.post(
            "/api/articles",
            json={
                "article": {
                    "title": f"Bench Article {uuid.uuid4().hex[:8]}",
                    "description": "Benchmark description",
                    "body": "Benchmark article body text",
                    "tagList": [],
                }
            },
            headers=self.headers,
            name="/api/articles [POST create]",
        )

    @task(1 if ACTIVE_TARGET == "pos_052_create_comment" else 0)
    def pos_052_create_comment_test(self):
        if not self.token or not self.article_slug:
            return
        self.client.post(
            f"/api/articles/{self.article_slug}/comments",
            json={"comment": {"body": f"benchmark comment {uuid.uuid4().hex[:8]}"}},
            headers=self.headers,
            name="/api/articles/:slug/comments [POST]",
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
