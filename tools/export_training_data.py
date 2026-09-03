#!/usr/bin/env python3
import argparse
import csv
import glob
import json
import os
import re
import subprocess

REGION = os.environ.get("AWS_REGION", "eu-central-1")
METRIC_FIELDS = [
    "p95_latency_ms",
    "avg_latency_ms",
    "requests_per_sec",
    "error_rate_percent",
    "total_requests",
    "total_failures",
]


def run_aws(args):
    proc = subprocess.run(
        ["aws", "--region", REGION, *args], capture_output=True, text=True
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "aws fehlgeschlagen")
    if not proc.stdout.strip():
        return None
    return json.loads(proc.stdout)


def fetch_s3_object(bucket, key):
    proc = subprocess.run(
        ["aws", "s3", "cp", f"s3://{bucket}/{key}", "-"], capture_output=True
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"Download fehlgeschlagen: {key}")
    return proc.stdout.decode("utf-8")


def list_metric_keys(bucket, variant):
    result = run_aws(
        [
            "s3api",
            "list-objects-v2",
            "--bucket",
            bucket,
            "--prefix",
            f"{variant}/",
        ]
    )
    keys = [c["Key"] for c in (result or {}).get("Contents", [])]
    return [k for k in keys if k.endswith("_metrics.json")]


def find_snippet_file(snippets_dir, pos):
    if not snippets_dir or not pos:
        return None
    matches = glob.glob(os.path.join(snippets_dir, f"[P01]_{pos}_*.py"))
    return matches[0] if matches else None


def extract_meta(key):
    parts = key.split("/")
    if len(parts) < 4:
        return None
    variant, method, env = parts[0], parts[1], parts[2]
    m = re.match(r"pos_(\d{3})", method)
    pos = m.group(1) if m else None
    return variant, method, env, pos


def main():
    parser = argparse.ArgumentParser(
        description="Exportiert KPI-JSONs aus S3 zu CSV + JSONL (mit Snippet-Code)"
    )
    parser.add_argument(
        "--bucket",
        default="kpi-save-bucket-415221799955-eu-central-1-an",
        help="S3-Bucket mit den KPI-Dateien",
    )
    parser.add_argument("--variant", default="v1", help="Varianten-Prefix im Bucket")
    parser.add_argument(
        "--snippets-dir",
        default="/Users/svenniederlohner/Desktop/DataRepositoryBachelor/ExtractedDataPositiveTraining/training_data_positive",
        help="Ordner mit den [P01]_NNN_*.py Snippet-Dateien",
    )
    parser.add_argument(
        "--out", default="export_kpis", help="Ausgabeordner (Default: export_kpis)"
    )
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    keys = list_metric_keys(args.bucket, args.variant)
    print(f"Gefundene KPI-Dateien: {len(keys)}")

    csv_path = os.path.join(args.out, "kpis.csv")
    jsonl_path = os.path.join(args.out, "dataset.jsonl")
    rows = []
    jsonl_lines = []
    missing_snippet = 0

    for key in keys:
        meta = extract_meta(key)
        if not meta:
            continue
        variant, method, env, pos = meta
        try:
            payload = json.loads(fetch_s3_object(args.bucket, key))
        except Exception as exc:
            print(f"  Warnung: {key} -> {exc}")
            continue

        row = {
            "variant": variant,
            "pos": pos or "",
            "method": method,
            "env": env,
            **{f: payload.get(f, "") for f in METRIC_FIELDS},
        }
        rows.append(row)

        snippet_file = find_snippet_file(args.snippets_dir, pos)
        snippet_code = ""
        if snippet_file:
            with open(snippet_file, encoding="utf-8", errors="replace") as fh:
                snippet_code = fh.read()
        else:
            missing_snippet += 1

        jsonl_lines.append(
            json.dumps(
                {
                    "variant": variant,
                    "pos": pos,
                    "method": method,
                    "env": env,
                    "metrics": {f: payload.get(f) for f in METRIC_FIELDS},
                    "snippet_file": snippet_file or "",
                    "snippet": snippet_code,
                },
                ensure_ascii=False,
            )
        )

    with open(jsonl_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(jsonl_lines))
        if jsonl_lines:
            fh.write("\n")

    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)

    print(f"CSV:  {csv_path}  ({len(rows)} Zeilen)")
    print(f"JSONL:{jsonl_path}  (KPI + Snippet je Zeile)")
    if missing_snippet:
        print(f"Hinweis: {missing_snippet} Eintraege ohne passendes Snippet-File")


if __name__ == "__main__":
    main()
