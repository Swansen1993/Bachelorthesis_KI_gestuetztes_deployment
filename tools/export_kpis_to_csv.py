import json
import os
import pathlib
import shutil
import subprocess
import tempfile

import pandas as pd

BUCKET = "kpi-save-bucket-415221799955-eu-central-1-an"
REGION = "eu-central-1"
EXCLUDE_PREFIXES = ("v1/",)
OUT_CSV = (
    pathlib.Path(
        "/Users/svenniederlohner/projects/Bachelorthesis_KI_gestuetztes_deployment"
    )
    / "export_kpis"
    / "all_projects_kpis_new.csv"
)
COLUMNS = [
    "variant",
    "env",
    "source",
    "avg_latency_ms",
    "error_rate_percent",
    "p95_latency_ms",
    "requests_per_sec",
    "target_method",
    "total_failures",
    "total_requests",
]
ENV_ORDER = ["low", "medium", "high", "extreme", "prod"]


def _run_aws(args):
    subprocess.run(
        ["aws", "--region", REGION, *args],
        check=True,
        capture_output=True,
        text=True,
    )


def _parse_metrics_file(abs_path, rel_path):
    parts = rel_path.parts
    variant = parts[0]
    method = parts[1]
    env = parts[2]
    with open(abs_path, encoding="utf-8") as fh:
        payload = json.load(fh)
    return {
        "variant": variant,
        "env": env,
        "source": str(rel_path),
        "target_method": method,
        "p95_latency_ms": payload.get("p95_latency_ms"),
        "avg_latency_ms": payload.get("avg_latency_ms"),
        "requests_per_sec": payload.get("requests_per_sec"),
        "error_rate_percent": payload.get("error_rate_percent"),
        "total_failures": payload.get("total_failures"),
        "total_requests": payload.get("total_requests"),
    }


def main():
    dump_dir = pathlib.Path(tempfile.mkdtemp(prefix="kpi_dump_"))
    try:
        exclude_args = []
        for prefix in EXCLUDE_PREFIXES:
            exclude_args += ["--exclude", f"{prefix}*"]
        _run_aws(
            [
                "s3",
                "sync",
                f"s3://{BUCKET}/",
                str(dump_dir),
                "--exclude",
                "*",
                "--include",
                "*metrics.json",
                *exclude_args,
            ]
        )
        rows = []
        for root, _dirs, files in os.walk(dump_dir):
            for name in files:
                if name.endswith("_metrics.json"):
                    full = pathlib.Path(root) / name
                    rel = full.relative_to(dump_dir)
                    rows.append(_parse_metrics_file(full, rel))
        df = pd.DataFrame(rows, columns=COLUMNS)
        df["env"] = pd.Categorical(df["env"], categories=ENV_ORDER, ordered=True)
        df = df.sort_values(["variant", "target_method", "env"]).reset_index(drop=True)
        OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(OUT_CSV, index=False)
        print(f"CSV geschrieben: {OUT_CSV}")
        print(f"Zeilen: {len(df)}")
        print(df["variant"].value_counts().sort_index().to_string())
    finally:
        shutil.rmtree(dump_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
