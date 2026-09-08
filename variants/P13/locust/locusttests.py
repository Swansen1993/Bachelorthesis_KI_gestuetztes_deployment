import os
import threading
import time
from locust import HttpUser, task, between, events
import boto3
import json

ACTIVE_TARGET = os.getenv("TARGET_METHOD", "pos_122_player_profile_ctrl")

PLAYER_ID = "28003"
CLUB_ID = "131"
COMP_ID = "FR1"


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


class Projekt13Tests(HttpUser):
    wait_time = between(0.1, 0.3)

    def _profile(self):
        self.client.get(f"/players/{PLAYER_ID}/profile", name="/players/:id/profile")

    def _market_value(self):
        self.client.get(
            f"/players/{PLAYER_ID}/market_value", name="/players/:id/market_value"
        )

    def _transfers(self):
        self.client.get(
            f"/players/{PLAYER_ID}/transfers", name="/players/:id/transfers"
        )

    def _stats(self):
        self.client.get(f"/players/{PLAYER_ID}/stats", name="/players/:id/stats")

    @task(1 if ACTIVE_TARGET == "pos_109_clubs_search" else 0)
    def pos_109_clubs_search_test(self):
        self.client.get("/clubs/search/FC", name="/clubs/search/:name")

    @task(1 if ACTIVE_TARGET == "pos_110_competitions_search" else 0)
    def pos_110_competitions_search_test(self):
        self.client.get(
            "/competitions/search/premier", name="/competitions/search/:name"
        )

    @task(1 if ACTIVE_TARGET == "pos_111_player_transfers" else 0)
    def pos_111_player_transfers_test(self):
        self._transfers()

    @task(1 if ACTIVE_TARGET == "pos_112_player_stats" else 0)
    def pos_112_player_stats_test(self):
        self._stats()

    @task(1 if ACTIVE_TARGET == "pos_113_player_profile" else 0)
    def pos_113_player_profile_test(self):
        self._profile()

    @task(1 if ACTIVE_TARGET == "pos_114_player_xpath" else 0)
    def pos_114_player_xpath_test(self):
        self._profile()

    @task(1 if ACTIVE_TARGET == "pos_115_clubs_search_service" else 0)
    def pos_115_clubs_search_service_test(self):
        self.client.get("/clubs/search/FC", name="/clubs/search/:name [service]")

    @task(1 if ACTIVE_TARGET == "pos_116_competitions_search_service" else 0)
    def pos_116_competitions_search_service_test(self):
        self.client.get(
            "/competitions/search/premier", name="/competitions/search/:name [service]"
        )

    @task(1 if ACTIVE_TARGET == "pos_117_player_profile_service" else 0)
    def pos_117_player_profile_service_test(self):
        self._profile()

    @task(1 if ACTIVE_TARGET == "pos_118_club_profile" else 0)
    def pos_118_club_profile_test(self):
        self.client.get(f"/clubs/{CLUB_ID}/profile", name="/clubs/:id/profile")

    @task(1 if ACTIVE_TARGET == "pos_119_player_market_value" else 0)
    def pos_119_player_market_value_test(self):
        self._market_value()

    @task(1 if ACTIVE_TARGET == "pos_120_player_transfers_service" else 0)
    def pos_120_player_transfers_service_test(self):
        self._transfers()

    @task(1 if ACTIVE_TARGET == "pos_121_player_stats_service" else 0)
    def pos_121_player_stats_service_test(self):
        self._stats()

    @task(1 if ACTIVE_TARGET == "pos_122_player_profile_ctrl" else 0)
    def pos_122_player_profile_ctrl_test(self):
        self._profile()

    @task(1 if ACTIVE_TARGET == "pos_123_player_market_value_ctrl" else 0)
    def pos_123_player_market_value_ctrl_test(self):
        self._market_value()

    @task(1 if ACTIVE_TARGET == "pos_124_player_transfers_ctrl" else 0)
    def pos_124_player_transfers_ctrl_test(self):
        self._transfers()

    @task(1 if ACTIVE_TARGET == "pos_125_player_stats_ctrl" else 0)
    def pos_125_player_stats_ctrl_test(self):
        self._stats()

    @task(1 if ACTIVE_TARGET == "pos_126_competitions_search_ctrl" else 0)
    def pos_126_competitions_search_ctrl_test(self):
        self.client.get(
            "/competitions/search/premier", name="/competitions/search/:name [ctrl]"
        )

    @task(1 if ACTIVE_TARGET == "pos_127_competition_clubs" else 0)
    def pos_127_competition_clubs_test(self):
        self.client.get(
            f"/competitions/{COMP_ID}/clubs", name="/competitions/:id/clubs"
        )

    @task(1 if ACTIVE_TARGET == "pos_128_players_search_ctrl" else 0)
    def pos_128_players_search_ctrl_test(self):
        self.client.get("/players/search/Lionel", name="/players/search/:name")


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
