import json
import pathlib
import re

import pandas as pd

ROOT = pathlib.Path(
    "/Users/svenniederlohner/projects/Bachelorthesis_KI_gestuetztes_deployment"
)
CSV_DIR = ROOT / "export_kpis" / "csv_kpis"
OUT_JSONL = ROOT / "export_kpis" / "dataset.jsonl"
SNIPPET_DIRS = {
    ("train", "pos"): ROOT / "snippets_training_pos",
    ("train", "neg"): ROOT / "snippets_training_neg",
    ("eval", "pos"): ROOT / "snippets_evaluation_pos",
    ("eval", "neg"): ROOT / "snippets_evaluation_neg",
}
EVAL_PROJECTS = {"P12", "P13"}
METRIC_FIELDS = [
    "avg_latency_ms",
    "error_rate_percent",
    "p95_latency_ms",
    "requests_per_sec",
    "total_failures",
    "total_requests",
]


def latest_csv():
    files = sorted(CSV_DIR.glob("all_projects_kpis_[0-9]*.csv"))
    if not files:
        raise FileNotFoundError(
            f"Keine Zeitstempel-KPI-CSV in {CSV_DIR} gefunden - zuerst exportieren."
        )
    return files[-1]


def index_snippets(folder):
    index = {}
    if not folder.exists():
        return index
    for f in folder.glob("*.py"):
        m = re.match(r"\[(P\d+)\]_(\d+)_(Pos|Neg)_", f.name)
        if m:
            polarity = m.group(3).lower()
            index[(m.group(1), m.group(2), polarity)] = f
    return index


def main():
    snippet_index = {
        split: index_snippets(folder) for split, folder in SNIPPET_DIRS.items()
    }
    csv_path = latest_csv()
    df = pd.read_csv(csv_path)
    print(f"Verwendete CSV: {csv_path}")
    df["pos"] = df["target_method"].str.extract(r"pos_(\d+)")

    lines = []
    missing = 0
    for _, r in df.iterrows():
        project = r["variant"].replace("_neg", "")
        is_neg = r["variant"].endswith("_neg")
        split = "eval" if project in EVAL_PROJECTS else "train"
        category = "neg" if is_neg else "pos"

        snippet_file = snippet_index[(split, category)].get(
            (project, str(r["pos"]), category)
        )
        snippet_code = ""
        if snippet_file is not None:
            snippet_code = snippet_file.read_text(encoding="utf-8", errors="replace")
        else:
            missing += 1

        lines.append(
            json.dumps(
                {
                    "variant": r["variant"],
                    "pos": str(r["pos"]),
                    "method": r["target_method"],
                    "env": r["env"],
                    "label": int(is_neg),
                    "split": split,
                    "metrics": {
                        f: (None if pd.isna(r[f]) else r[f]) for f in METRIC_FIELDS
                    },
                    "snippet_file": str(snippet_file) if snippet_file else "",
                    "snippet": snippet_code,
                },
                ensure_ascii=False,
            )
        )

    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSONL, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
        if lines:
            fh.write("\n")

    print(f"JSONL geschrieben: {OUT_JSONL}")
    print(f"Zeilen: {len(lines)}")
    print(f"Davon ohne Snippet-Code: {missing}")
    labels = {}
    for line in lines:
        d = json.loads(line)
        labels[d["label"]] = labels.get(d["label"], 0) + 1
    print(f"Label-Verteilung: {labels}")


if __name__ == "__main__":
    main()
