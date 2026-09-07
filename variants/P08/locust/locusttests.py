import os
import threading
import time
import uuid
from locust import HttpUser, task, between, events
import boto3
import json

ACTIVE_TARGET = os.getenv("TARGET_METHOD", "pos_062_create_product")

ORDER_TARGETS = [
    "pos_063_create_order_from_cart",
    "pos_067_create_order_controller",
]


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


class Projekt08Tests(HttpUser):
    wait_time = between(0.1, 0.3)

    def _signup(self, name, email, password, role=None):
        body = {"name": name, "email": email, "password": password}
        if role:
            body["role"] = role
        res = self.client.post(
            "/signup",
            json=body,
            name="/signup [seed]",
        )
        return res.status_code in (200, 201)

    def _login(self, email, password):
        res = self.client.post(
            "/login",
            data={"username": email, "password": password},
            name="/login [seed]",
        )
        if res.status_code == 200:
            return res.json().get("access_token")
        return None

    def _headers(self, token):
        return {"Authorization": f"Bearer {token}"}

    def _create_category(self, headers, label):
        res = self.client.post(
            "/categories/",
            json={"name": f"{label} {uuid.uuid4().hex[:8]}", "description": "benchmark"},
            headers=headers,
            name="/categories/ [seed]",
        )
        if res.status_code in (200, 201):
            return res.json().get("id")
        return None

    def _create_product(self, headers, category_id):
        res = self.client.post(
            "/products/",
            json={
                "name": f"Seed Product {uuid.uuid4().hex[:8]}",
                "price": 10.0,
                "stock": 1000000,
                "category_id": category_id,
            },
            headers=headers,
            name="/products/ [seed]",
        )
        if res.status_code in (200, 201):
            return res.json().get("id")
        return None

    def _create_address(self, headers):
        self.client.post(
            "/addresses/",
            json={
                "street": "Bench Street 1",
                "city": "Berlin",
                "state": "BE",
                "country": "DE",
                "postal_code": "10115",
            },
            headers=headers,
            name="/addresses/ [seed]",
        )

    def _setup_seller(self):
        email = f"seller_{uuid.uuid4().hex[:8]}@test.com"
        password = "pass1234"
        self._signup(f"Seller {uuid.uuid4().hex[:8]}", email, password, role="seller")
        token = self._login(email, password)
        return self._headers(token) if token else {}

    def _setup_customer(self):
        self.email = f"cust_{uuid.uuid4().hex[:8]}@test.com"
        self.password = "pass1234"
        self._signup(f"Cust {uuid.uuid4().hex[:8]}", self.email, self.password)
        token = self._login(self.email, self.password)
        return self._headers(token) if token else {}

    def on_start(self):
        self.seller_headers = {}
        self.customer_headers = {}
        self.category_id = None
        self.product_id = None
        self.email = ""
        self.password = ""
        if ACTIVE_TARGET == "pos_062_create_product":
            self.seller_headers = self._setup_seller()
            self.category_id = self._create_category(self.seller_headers, "Cat")
        elif ACTIVE_TARGET == "pos_064_admin_or_seller":
            self.seller_headers = self._setup_seller()
        elif ACTIVE_TARGET in ORDER_TARGETS:
            self.seller_headers = self._setup_seller()
            self.category_id = self._create_category(self.seller_headers, "Cat")
            self.product_id = self._create_product(self.seller_headers, self.category_id)
            self.customer_headers = self._setup_customer()
            self._create_address(self.customer_headers)
        elif ACTIVE_TARGET == "pos_065_login":
            self._setup_customer()

    @task(1 if ACTIVE_TARGET == "pos_062_create_product" else 0)
    def pos_062_create_product_test(self):
        if not self.seller_headers or not self.category_id:
            return
        self.client.post(
            "/products/",
            json={
                "name": f"Bench Product {uuid.uuid4().hex[:8]}",
                "price": 10.0,
                "stock": 1000,
                "category_id": self.category_id,
            },
            headers=self.seller_headers,
            name="/products/ [POST create]",
        )

    @task(1 if ACTIVE_TARGET == "pos_063_create_order_from_cart" else 0)
    def pos_063_create_order_from_cart_test(self):
        if not self.customer_headers or not self.product_id:
            return
        self.client.post(
            "/cart/items",
            json={"product_id": self.product_id, "quantity": 1},
            headers=self.customer_headers,
            name="/cart/items [POST add]",
        )
        self.client.post(
            "/orders/",
            headers=self.customer_headers,
            name="/orders/ [POST create]",
        )

    @task(1 if ACTIVE_TARGET == "pos_064_admin_or_seller" else 0)
    def pos_064_admin_or_seller_test(self):
        if not self.seller_headers:
            return
        self.client.post(
            "/categories/",
            json={"name": f"Cat {uuid.uuid4().hex[:8]}", "description": "benchmark"},
            headers=self.seller_headers,
            name="/categories/ [POST create]",
        )

    @task(1 if ACTIVE_TARGET == "pos_065_login" else 0)
    def pos_065_login_test(self):
        if not self.email:
            return
        self.client.post(
            "/login",
            data={"username": self.email, "password": self.password},
            name="/login [POST]",
        )

    @task(1 if ACTIVE_TARGET == "pos_066_signup" else 0)
    def pos_066_signup_test(self):
        self.client.post(
            "/signup",
            json={
                "name": f"New User {uuid.uuid4().hex[:8]}",
                "email": f"{uuid.uuid4().hex[:8]}@test.com",
                "password": "pass1234",
            },
            name="/signup [POST]",
        )

    @task(1 if ACTIVE_TARGET == "pos_067_create_order_controller" else 0)
    def pos_067_create_order_controller_test(self):
        if not self.customer_headers or not self.product_id:
            return
        self.client.post(
            "/cart/items",
            json={"product_id": self.product_id, "quantity": 1},
            headers=self.customer_headers,
            name="/cart/items [POST add]",
        )
        self.client.post(
            "/orders/",
            headers=self.customer_headers,
            name="/orders/ [POST create]",
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
