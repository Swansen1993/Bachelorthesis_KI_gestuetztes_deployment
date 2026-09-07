#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MAPPING = os.path.join(SCRIPT_DIR, "tests.json")

REGION = os.environ.get("AWS_REGION", "eu-central-1")

CONTAINER_APP = "Application_container"
CONTAINER_LOCUST = "locust_test_runner"

LOG_APP = "/ecs/app-{env}"
LOG_LOCUST = "/ecs/locust-{env}"

DB_CLEAN_CMD = (
    "import asyncio, asyncpg, os\n"
    "async def _clean():\n"
    "    c = await asyncpg.connect(host=os.environ['POSTGRES_HOST'], port=int(os.environ['POSTGRES_PORT']), "
    "user=os.environ['POSTGRES_USER'], password=os.environ['POSTGRES_PASSWORD'], database=os.environ['POSTGRES_DB'])\n"
    "    rows = await c.fetch(\"SELECT tablename FROM pg_tables WHERE schemaname='public'\")\n"
    "    for r in rows:\n"
    "        if r['tablename'] == 'alembic_version':\n"
    "            continue\n"
    "        await c.execute('TRUNCATE TABLE \"' + r['tablename'] + '\" RESTART IDENTITY CASCADE')\n"
    "    await c.close()\n"
    "loop = asyncio.new_event_loop()\n"
    "asyncio.set_event_loop(loop)\n"
    "loop.run_until_complete(_clean())\n"
    "loop.close()"
)


def run_aws(args, check=True):
    cmd = ["aws", "--region", REGION, *args]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        msg = proc.stderr.strip() or proc.stdout.strip() or "unbekannter Fehler"
        if check:
            raise RuntimeError(f"aws {' '.join(args)} fehlgeschlagen: {msg}")
        print(f"  (Warnung) aws {' '.join(args)}: {msg}")
        return None
    if not proc.stdout.strip():
        return None
    return json.loads(proc.stdout)


def load_env_infos(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_test_mapping(path=DEFAULT_MAPPING):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def resolve_mapping(explicit=None):
    if explicit:
        return explicit
    variant = os.environ.get("VARIANT_ID", "")
    candidate = os.path.join("variants", variant, "tests.json")
    if os.path.isfile(candidate):
        return candidate
    return DEFAULT_MAPPING


def network_config(env_info):
    return {
        "awsvpcConfiguration": {
            "subnets": [env_info["subnet_id"]],
            "securityGroups": [env_info["security_group_id"]],
            "assignPublicIp": "ENABLED",
        }
    }


def run_task_and_wait(env_info, task_family, overrides, timeout_s, log_group, label):
    cluster = env_info["cluster_name"]
    netcfg = json.dumps(network_config(env_info))
    overrides_json = json.dumps({"containerOverrides": overrides})

    print(f"[{label}] Starte Task (cluster={cluster}, task-def={task_family})")
    result = run_aws(
        [
            "ecs",
            "run-task",
            "--cluster",
            cluster,
            "--task-definition",
            task_family,
            "--launch-type",
            "FARGATE",
            "--network-configuration",
            netcfg,
            "--overrides",
            overrides_json,
        ]
    )
    tasks = (result or {}).get("tasks", [])
    if not tasks:
        print(
            f"[{label}] FEHLER: run-task hat keinen Task zurueckgegeben "
            "(IAM/Berechtigungen der CI-Rolle pruefen)."
        )
        return False
    task_arn = tasks[0]["taskArn"]
    print(f"[{label}] taskArn={task_arn}")

    waited = 0
    last_status = "UNKNOWN"
    while waited < timeout_s:
        desc = run_aws(
            ["ecs", "describe-tasks", "--cluster", cluster, "--tasks", task_arn]
        )
        task = (desc or {}).get("tasks", [{}])[0]
        last_status = task.get("lastStatus", "UNKNOWN")
        print(f"[{label}] Status: {last_status}")
        if last_status == "STOPPED":
            break
        time.sleep(10)
        waited += 10

    if last_status != "STOPPED":
        print(f"[{label}] FEHLER: Timeout nach {timeout_s}s - Task nicht beendet.")
        dump_logs(log_group)
        return False

    desc = run_aws(["ecs", "describe-tasks", "--cluster", cluster, "--tasks", task_arn])
    task = (desc or {}).get("tasks", [{}])[0]
    containers = task.get("containers", [])
    exit_code = containers[0].get("exitCode") if containers else None
    stop_code = task.get("stopCode", "")
    stopped_reason = task.get("stoppedReason", "")

    print(f"[{label}] stopCode={stop_code}, exitCode={exit_code}")
    if exit_code == 0:
        print(f"[{label}] OK")
        return True

    print(f"[{label}] FEHLER: exitCode={exit_code} ({stopped_reason})")
    dump_logs(log_group)
    return False


def dump_logs(log_group):
    try:
        streams = run_aws(
            [
                "logs",
                "describe-log-streams",
                "--log-group-name",
                log_group,
                "--order-by",
                "LastEventTime",
                "--descending",
                "--max-items",
                "1",
            ],
            check=False,
        )
        stream_name = ((streams or {}).get("logStreams") or [{}])[0].get(
            "logStreamName"
        )
        if not stream_name:
            return
        events = run_aws(
            [
                "logs",
                "get-log-events",
                "--log-group-name",
                log_group,
                "--log-stream-name",
                stream_name,
            ],
            check=False,
        )
        messages = [
            (e or {}).get("message", "") for e in (events or {}).get("events", [])
        ]
        print("----- Letzte Logs -----")
        print("\n".join(messages[-30:]))
    except Exception as exc:
        print(f"  (Logs konnten nicht geladen werden: {exc})")


def cmd_clean(args):
    env_infos = load_env_infos(args.env_info)
    if args.env not in env_infos:
        print(
            f"Umgebung '{args.env}' nicht in environment_infos.json gefunden. "
            f"Vorhanden: {sorted(env_infos)}"
        )
        return 1
    info = env_infos[args.env]

    overrides = [
        {
            "name": CONTAINER_APP,
            "command": ["python", "-c", DB_CLEAN_CMD],
        }
    ]

    ok = run_task_and_wait(
        info,
        info["app_task_family"],
        overrides,
        timeout_s=args.timeout,
        log_group=LOG_APP.format(env=args.env),
        label=f"db-clean-{args.env}",
    )
    return 0 if ok else 1


def cmd_migrate(args):
    env_infos = load_env_infos(args.env_info)
    if args.env not in env_infos:
        print(
            f"Umgebung '{args.env}' nicht in environment_infos.json gefunden. "
            f"Vorhanden: {sorted(env_infos)}"
        )
        return 1
    info = env_infos[args.env]

    config = load_test_mapping(resolve_mapping(args.mapping))
    migrate_cmd = config.get("db_migrate")
    if not migrate_cmd:
        print(
            f"FEHLER: Kein 'db_migrate'-Kommando in {args.mapping} konfiguriert. "
            f"Bitte pro Repo eintragen."
        )
        return 1

    overrides = [{"name": CONTAINER_APP, "command": migrate_cmd}]

    ok = run_task_and_wait(
        info,
        info["app_task_family"],
        overrides,
        timeout_s=args.timeout,
        log_group=LOG_APP.format(env=args.env),
        label=f"db-migrate-{args.env}",
    )
    return 0 if ok else 1


def cmd_seed(args):
    env_infos = load_env_infos(args.env_info)
    if args.env not in env_infos:
        print(
            f"Umgebung '{args.env}' nicht in environment_infos.json gefunden. "
            f"Vorhanden: {sorted(env_infos)}"
        )
        return 1
    info = env_infos[args.env]

    config = load_test_mapping(resolve_mapping(args.mapping))
    seed_cmd = config.get("db_seed")
    if not seed_cmd:
        print(
            f"Kein 'db_seed'-Kommando in {args.mapping} konfiguriert - Seed uebersprungen."
        )
        return 0

    overrides = [{"name": CONTAINER_APP, "command": seed_cmd}]

    ok = run_task_and_wait(
        info,
        info["app_task_family"],
        overrides,
        timeout_s=args.timeout,
        log_group=LOG_APP.format(env=args.env),
        label=f"db-seed-{args.env}",
    )
    return 0 if ok else 1


def cmd_run(args):
    env_infos = load_env_infos(args.env_info)
    if args.env not in env_infos:
        print(
            f"Umgebung '{args.env}' nicht in environment_infos.json gefunden. "
            f"Vorhanden: {sorted(env_infos)}"
        )
        return 1
    info = env_infos[args.env]

    mapping = load_test_mapping(resolve_mapping(args.mapping))
    test_names = sorted(k for k in mapping if not k.startswith("db_"))
    if args.test not in mapping:
        print(
            f"Test '{args.test}' nicht in {args.mapping} gefunden. "
            f"Vorhanden: {test_names}"
        )
        return 1
    method = mapping[args.test]

    variant = args.variant or os.environ.get("VARIANT_ID", "P01")
    metrics_file = f"{method}_{args.env}_metrics.json"
    s3_path = f"{variant}/{method}/{args.env}/{metrics_file}"

    print(f"[locust-{args.env}] Test={args.test} -> Methode={method}")
    print(f"[locust-{args.env}] S3-KPI-Pfad: {s3_path}")

    overrides = [
        {
            "name": CONTAINER_LOCUST,
            "environment": [
                {"name": "TARGET_METHOD", "value": method},
                {"name": "S3_METRICS_PATH", "value": s3_path},
            ],
        }
    ]

    ok = run_task_and_wait(
        info,
        info["runner_task_family"],
        overrides,
        timeout_s=args.timeout,
        log_group=LOG_LOCUST.format(env=args.env),
        label=f"locust-{args.env}",
    )
    return 0 if ok else 1


def cmd_benchmark(args):
    env_infos = load_env_infos(args.env_info)
    config = load_test_mapping(resolve_mapping(args.mapping))
    if args.test not in config:
        print(
            f"Test '{args.test}' nicht in tests.json gefunden. "
            f"Vorhanden: {sorted(k for k in config if not k.startswith('db_'))}"
        )
        return 1

    envs = sorted(env_infos)

    def worker(env):
        ns = argparse.Namespace(
            env_info=args.env_info,
            env=env,
            timeout=args.timeout,
            mapping=args.mapping,
            test=args.test,
            variant=args.variant,
        )
        ok = cmd_migrate(ns) == 0
        if ok:
            ok = cmd_clean(ns) == 0
        if ok:
            ok = cmd_seed(ns) == 0
        if ok:
            ok = cmd_run(ns) == 0
        return env, ok

    results = {}
    with ThreadPoolExecutor(max_workers=min(6, len(envs))) as pool:
        futures = {pool.submit(worker, env): env for env in envs}
        for future in futures:
            env, ok = future.result()
            results[env] = ok

    failed = [env for env, ok in results.items() if not ok]
    for env in sorted(results):
        print(f"[benchmark-{env}] {'OK' if results[env] else 'FEHLER'}")
    if failed:
        print(f"FEHLGESCHLAGENE Umgebungen fuer {args.test}: {failed}")
        return 1
    print(f"[benchmark] {args.test}: alle Umgebungen OK ({len(envs)})")
    return 0


def main():
    parser = argparse.ArgumentParser(description="ECS One-off-Task Helfer")
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--env-info", required=True, help="Pfad zur environment_infos.json (Artifact)"
    )
    common.add_argument(
        "--env", required=True, help="Umgebung (z. B. low, medium, high, extreme)"
    )

    p_clean = sub.add_parser(
        "clean", parents=[common], help="DB leeren (alle Daten entfernen)"
    )
    p_clean.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Maximale Wartezeit in Sekunden (Default 300)",
    )
    p_clean.set_defaults(func=cmd_clean)

    p_migrate = sub.add_parser(
        "migrate", parents=[common], help="DB-Schema migrieren (Kommando aus Konfig)"
    )
    p_migrate.add_argument(
        "--mapping",
        default=None,
        help="Pfad zur Konfig mit db_migrate (Default: variante/variants tests.json)",
    )
    p_migrate.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Maximale Wartezeit in Sekunden (Default 300)",
    )
    p_migrate.set_defaults(func=cmd_migrate)

    p_run = sub.add_parser(
        "run", parents=[common], help="Locust-Runner-Task ausfuehren"
    )
    p_run.add_argument(
        "--test",
        required=True,
        help="Generischer Testname aus tests.json (z. B. Locust-Test-1)",
    )
    p_run.add_argument(
        "--mapping",
        default=None,
        help="Pfad zur tests.json (Default: variante/variants tests.json)",
    )
    p_run.add_argument(
        "--variant",
        default=None,
        help="Varianten-ID fuer den S3-Pfad (Default: env VARIANT_ID oder P01)",
    )
    p_run.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Maximale Wartezeit in Sekunden (Default 600)",
    )
    p_run.set_defaults(func=cmd_run)

    p_benchmark = sub.add_parser(
        "benchmark", help="Einen Test in allen Umgebungen parallel ausfuehren"
    )
    p_benchmark.add_argument(
        "--env-info", required=True, help="Pfad zur environment_infos.json (Artifact)"
    )
    p_benchmark.add_argument(
        "--test",
        required=True,
        help="Generischer Testname aus tests.json (z. B. Locust-Test-1)",
    )
    p_benchmark.add_argument(
        "--mapping",
        default=None,
        help="Pfad zur tests.json (Default: variante/variants tests.json)",
    )
    p_benchmark.add_argument(
        "--variant",
        default=None,
        help="Varianten-ID fuer den S3-Pfad (Default: env VARIANT_ID oder P01)",
    )
    p_benchmark.add_argument(
        "--timeout",
        type=int,
        default=900,
        help="Maximale Wartezeit je env-Schritt in Sekunden (Default 900)",
    )
    p_benchmark.set_defaults(func=cmd_benchmark)

    args = parser.parse_args()
    try:
        sys.exit(args.func(args))
    except RuntimeError as exc:
        print(f"FEHLER: {exc}")
        sys.exit(1)
    except FileNotFoundError as exc:
        print(f"FEHLER: Datei nicht gefunden - {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
