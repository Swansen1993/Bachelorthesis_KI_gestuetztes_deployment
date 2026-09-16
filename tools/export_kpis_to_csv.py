import argparse
import datetime
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
OUT_DIR = (
    pathlib.Path(
        "/Users/svenniederlohner/projects/Bachelorthesis_KI_gestuetztes_deployment"
    )
    / "export_kpis"
    / "csv_kpis"
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


def _sync_bucket(dump_dir, methods):
    include_args = ["--include", "*metrics.json"]
    if methods:
        include_args = []
        for method in methods:
            include_args += ["--include", f"*{method}*metrics.json"]
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
            *include_args,
            *exclude_args,
        ]
    )


def _collect_rows(dump_dir):
    rows = []
    for root, _dirs, files in os.walk(dump_dir):
        for name in files:
            if name.endswith("_metrics.json"):
                full = pathlib.Path(root) / name
                rel = full.relative_to(dump_dir)
                rows.append(_parse_metrics_file(full, rel))
    return rows


def _merge_with_reference(df, pattern, reference_csv):
    if not pattern or not reference_csv.exists():
        return df
    existing = pd.read_csv(reference_csv)
    keep = ~existing["target_method"].str.contains(pattern, regex=True)
    return pd.concat([existing.loc[keep, COLUMNS], df[COLUMNS]], ignore_index=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--only",
        nargs="*",
        default=None,
        help="Nur Methoden mit diesem Teilstring aus S3 holen und in die bestehende CSV mergen",
    )
    args = parser.parse_args()
    pattern = "|".join(args.only) if args.only else None

    dump_dir = pathlib.Path(tempfile.mkdtemp(prefix="kpi_dump_"))
    try:
        _sync_bucket(dump_dir, args.only)
        new_csv = OUT_DIR / "all_projects_kpis_new.csv"
        df = pd.DataFrame(_collect_rows(dump_dir), columns=COLUMNS)
        df = _merge_with_reference(df, pattern, new_csv)
        df["env"] = pd.Categorical(df["env"], categories=ENV_ORDER, ordered=True)
        df = df.sort_values(["variant", "target_method", "env"]).reset_index(drop=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_csv = OUT_DIR / f"all_projects_kpis_{timestamp}.csv"
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_csv, index=False)
        df.to_csv(new_csv, index=False)
        print(f"CSV geschrieben: {out_csv}")
        print(f"Referenz aktualisiert: {new_csv}")
        print(f"Zeilen: {len(df)}")
        if pattern:
            print(
                df[df["target_method"].str.contains(pattern, regex=True)].to_string(
                    index=False
                )
            )
        else:
            print(df["variant"].value_counts().sort_index().to_string())
    finally:
        shutil.rmtree(dump_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
