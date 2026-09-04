import os
import threading
import time
import uuid
from locust import HttpUser, task, between, events, stats
import boto3
import json

ACTIVE_TARGET = os.getenv("TARGET_METHOD", "pos_022_create_note")


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


class Projekt02Tests(HttpUser):
    wait_time = between(0.1, 0.3)

    def on_start(self):
        self.notebook_id = None
        self.note_id = None

        nb_res = self.client.post(
            "/api/notebooks",
            json={"title": f"Bench Notebook {uuid.uuid4().hex[:8]}", "notes": []},
            name="/api/notebooks [POST seed]",
        )
        if nb_res.status_code in [200, 201]:
            self.notebook_id = nb_res.json().get("id")

        if self.notebook_id:
            note_res = self.client.post(
                "/api/notes",
                json={
                    "title": f"Seed Note {uuid.uuid4().hex[:8]}",
                    "content": "Benchmark seed note",
                    "notebook_id": self.notebook_id,
                },
                name="/api/notes [POST seed]",
            )
            if note_res.status_code in [200, 201]:
                self.note_id = note_res.json().get("id")

    @task(1 if ACTIVE_TARGET == "pos_022_create_note" else 0)
    def create_note_test(self):
        if not self.notebook_id:
            return
        self.client.post(
            "/api/notes",
            json={
                "title": f"Note {uuid.uuid4().hex[:8]}",
                "content": "Benchmark note content",
                "notebook_id": self.notebook_id,
            },
            name="/api/notes [POST create]",
        )

    @task(1 if ACTIVE_TARGET == "pos_023_read_all_notes" else 0)
    def read_all_notes_test(self):
        self.client.get(
            "/api/notes",
            name="/api/notes [GET list]",
        )

    @task(1 if ACTIVE_TARGET == "pos_024_read_note" else 0)
    def read_note_test(self):
        if not self.note_id:
            return
        self.client.get(
            f"/api/notes/{self.note_id}",
            name="/api/notes/:id [GET]",
        )

    @task(1 if ACTIVE_TARGET == "pos_025_update_note" else 0)
    def update_note_test(self):
        if not self.note_id:
            return
        self.client.put(
            f"/api/notes/{self.note_id}",
            json={
                "title": f"Updated {uuid.uuid4().hex[:8]}",
                "content": "Updated benchmark note content",
                "notebook_id": self.notebook_id,
            },
            name="/api/notes/:id [PUT update]",
        )

    @task(1 if ACTIVE_TARGET == "pos_026_delete_note" else 0)
    def delete_note_test(self):
        nb_res = self.client.post(
            "/api/notebooks",
            json={"title": f"Setup {uuid.uuid4().hex[:8]}", "notes": []},
            name="/api/notebooks [POST setup]",
        )
        if nb_res.status_code not in [200, 201]:
            return
        nb_id = nb_res.json().get("id")
        note_res = self.client.post(
            "/api/notes",
            json={
                "title": f"Delete {uuid.uuid4().hex[:8]}",
                "content": "Delete benchmark note",
                "notebook_id": nb_id,
            },
            name="/api/notes [POST setup]",
        )
        if note_res.status_code in [200, 201]:
            note_id = note_res.json().get("id")
            self.client.delete(
                f"/api/notes/{note_id}",
                name="/api/notes/:id [DELETE]",
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
