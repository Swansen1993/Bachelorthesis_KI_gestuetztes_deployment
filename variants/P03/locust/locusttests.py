import os
import threading
import time
import uuid
from locust import HttpUser, task, between, events, stats
import boto3
import json

ACTIVE_TARGET = os.getenv("TARGET_METHOD", "pos_027_post_mail")


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


class Projekt03Tests(HttpUser):
    wait_time = between(0.1, 0.3)

    def _mail_payload(self):
        return {
            "email": f"user_{uuid.uuid4().hex[:8]}@test.com",
            "name": "Benchmark User",
            "subject": "Benchmark mail subject",
            "message": "Benchmark mail message body",
            "honeypot": "",
        }

    @task(1 if ACTIVE_TARGET in ["pos_027_post_mail", "pos_028_send_email"] else 0)
    def post_mail_test(self):
        self.client.post(
            "/api/mail",
            json=self._mail_payload(),
            name=f"/api/mail [POST {ACTIVE_TARGET}]",
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
