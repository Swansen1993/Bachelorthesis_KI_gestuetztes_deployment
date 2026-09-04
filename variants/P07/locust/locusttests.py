import os
import threading
import time
import uuid
from locust import HttpUser, task, between, events
import boto3
import json

ACTIVE_TARGET = os.getenv("TARGET_METHOD", "pos_054_get_product_by_id")
PRODUCT_ID = int(os.getenv("SEED_PRODUCT_ID", "1"))


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


class Projekt07Tests(HttpUser):
    wait_time = between(0.1, 0.3)

    def _sales_base(self):
        if ":8080" in self.host:
            return self.host.replace(":8080", ":8081")
        return self.host

    def _seed_sale(self):
        self.client.post(
            f"{self._sales_base()}/sales/create/",
            json={
                "product_id": PRODUCT_ID,
                "category_name": "electronics",
                "units_sold": 1,
            },
            name="/sales/create/ [seed]",
        )

    def on_start(self):
        if ACTIVE_TARGET in (
            "pos_053_fetch_sales",
            "pos_061_retrieve_sales",
        ):
            self._seed_sale()

    @task(1 if ACTIVE_TARGET == "pos_053_fetch_sales" else 0)
    def pos_053_fetch_sales_test(self):
        self.client.post(
            f"{self._sales_base()}/sales/retrieve_sales",
            json={"product_id": PRODUCT_ID},
            name="/sales/retrieve_sales [fetch_sales]",
        )

    @task(1 if ACTIVE_TARGET == "pos_054_get_product_by_id" else 0)
    def pos_054_get_product_by_id_test(self):
        self.client.get(
            f"/products/get_product/?product_id={PRODUCT_ID}",
            name="/products/get_product/ [get_product]",
        )

    @task(1 if ACTIVE_TARGET == "pos_055_inventory_history" else 0)
    def pos_055_inventory_history_test(self):
        self.client.get(
            f"/products/inventory_history?product_id={PRODUCT_ID}",
            name="/products/inventory_history [get_history]",
        )

    @task(1 if ACTIVE_TARGET == "pos_056_create_sale_transaction" else 0)
    def pos_056_create_sale_transaction_test(self):
        self.client.post(
            f"{self._sales_base()}/sales/create/",
            json={
                "product_id": PRODUCT_ID,
                "category_name": "electronics",
                "units_sold": 1,
            },
            name="/sales/create/ [sale_transaction]",
        )

    @task(1 if ACTIVE_TARGET == "pos_057_create_product" else 0)
    def pos_057_create_product_test(self):
        self.client.post(
            "/products/create/",
            json={
                "name": f"Bench Product {uuid.uuid4().hex[:8]}",
                "description": "Benchmark product",
                "price": 50.0,
                "image": "http://localhost/img.png",
                "category_name": "electronics",
                "current_inventory": 1000,
            },
            name="/products/create/ [create_product]",
        )

    @task(1 if ACTIVE_TARGET == "pos_058_update_product_attribute" else 0)
    def pos_058_update_product_attribute_test(self):
        self.client.put(
            f"/products/update?product_id={PRODUCT_ID}",
            json={
                "price": 99.0,
                "current_inventory": 900000000,
            },
            name="/products/update [update_attribute]",
        )

    @task(1 if ACTIVE_TARGET == "pos_059_create_sale" else 0)
    def pos_059_create_sale_test(self):
        self.client.post(
            f"{self._sales_base()}/sales/create/",
            json={
                "product_id": PRODUCT_ID,
                "category_name": "electronics",
                "units_sold": 1,
            },
            name="/sales/create/ [create_sale]",
        )

    @task(1 if ACTIVE_TARGET == "pos_060_update_product" else 0)
    def pos_060_update_product_test(self):
        self.client.put(
            f"/products/update?product_id={PRODUCT_ID}",
            json={
                "price": 98.0,
                "current_inventory": 800000000,
            },
            name="/products/update [update_product]",
        )

    @task(1 if ACTIVE_TARGET == "pos_061_retrieve_sales" else 0)
    def pos_061_retrieve_sales_test(self):
        self.client.post(
            f"{self._sales_base()}/sales/retrieve_sales",
            json={"product_id": PRODUCT_ID},
            name="/sales/retrieve_sales [retrieve]",
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
