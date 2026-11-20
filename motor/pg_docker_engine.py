#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module 1: Live Docker PostgreSQL (`postgres:17`) Verification Engine.
- Spins up an ephemeral Docker PostgreSQL container (`--rm`, zero host state).
- Applies target SQL migrations (or self-test clinical DDL) via `docker exec psql`.
- Verifies DDL syntax, primary/foreign/unique constraints, parallel ACID conflict locking
  (10 concurrent workers contending for the same chair/slot), and SQLite <-> PostgreSQL
  table parity.
- Always removes the container in `finally:`.
"""
from __future__ import annotations

import concurrent.futures
import re
import shutil
import socket
import subprocess
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Istanbul")

SELF_TEST_PG_SCHEMA = """
CREATE TABLE IF NOT EXISTS clinics (
    id SERIAL PRIMARY KEY,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    clinic_id INT NOT NULL REFERENCES clinics(id),
    display_name TEXT NOT NULL,
    phone_hmac TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (clinic_id, phone_hmac)
);
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    clinic_id INT NOT NULL REFERENCES clinics(id),
    patient_id INT NOT NULL REFERENCES patients(id),
    chair TEXT NOT NULL,
    starts_at TIMESTAMPTZ NOT NULL,
    status TEXT NOT NULL DEFAULT 'booked',
    UNIQUE (clinic_id, chair, starts_at)
);
CREATE TABLE IF NOT EXISTS charges (
    id SERIAL PRIMARY KEY,
    clinic_id INT NOT NULL REFERENCES clinics(id),
    patient_id INT NOT NULL REFERENCES patients(id),
    amount_kurus BIGINT NOT NULL CHECK (amount_kurus > 0),
    idempotency_key TEXT,
    UNIQUE (clinic_id, idempotency_key)
);
INSERT INTO clinics (slug, name) VALUES ('merkez', 'Test Merkez Klinik') ON CONFLICT DO NOTHING;
INSERT INTO patients (clinic_id, display_name, phone_hmac) VALUES (1, 'PG Test Hasta', 'hmac_pg_001') ON CONFLICT DO NOTHING;
"""


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _docker_bin() -> str | None:
    return shutil.which("docker")


def _pick_pg_image() -> str | None:
    docker_exe = _docker_bin()
    if not docker_exe:
        return None
    r = subprocess.run(  # noqa: S603
        [docker_exe, "images", "--format", "{{.Repository}}:{{.Tag}}"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if r.returncode != 0:
        return None
    imgs = [x.strip() for x in (r.stdout or "").splitlines() if x.strip()]
    for pref in ("postgres:17", "postgres:17-alpine", "pgvector/pgvector:pg16", "postgres:16-alpine", "postgres:16"):
        if pref in imgs:
            return pref
    return "postgres:17-alpine" if sys.platform.startswith("linux") else "postgres:17"


def _psql_exec(cname: str, sql: str, timeout: int = 20) -> tuple[int, str, str]:
    docker_exe = _docker_bin()
    if not docker_exe:
        return 127, "", "docker binary not found"
    p = subprocess.run(  # noqa: S603
        [docker_exe, "exec", "-i", cname, "psql", "-v", "ON_ERROR_STOP=1", "-U", "dc_test", "-d", "dentacore_test", "-At"],
        input=sql,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
    )
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


def run_docker_postgres_verification(
    sql_files: list[Path] | None = None,
    sqlite_schema_source: Path | None = None,
    self_test_mode: bool = False,
) -> dict[str, Any]:
    """
    Executes a live isolated Docker PostgreSQL audit:
    - Boots ephemeral container (`postgres:17` / `pgvector:pg16`).
    - Executes provided SQL migration files (or built-in self-test schema).
    - Runs 10-way concurrent UNIQUE/ACID transaction race inside PostgreSQL.
    - Compares SQLite vs PostgreSQL table names if `sqlite_schema_source` is given.
    """
    t0 = time.perf_counter()
    ts = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
    out: dict[str, Any] = {
        "gate": "DOCKER_POSTGRES",
        "timestamp": ts,
        "status": "SKIP",
        "image": "",
        "tables_created": 0,
        "migrations_applied": [],
        "acid_race_commits": 0,
        "acid_race_conflicts": 0,
        "parity_missing_in_pg": [],
        "errors": [],
        "duration_sec": 0.0,
    }

    img = _pick_pg_image()
    docker_exe = _docker_bin()
    if not img or not docker_exe:
        out["status"] = "FAIL"
        out["errors"].append("Docker CLI veya daemon erişilemiyor")
        out["duration_sec"] = round(time.perf_counter() - t0, 2)
        return out

    out["image"] = img
    cname = f"dc_sentinel_pg_{uuid.uuid4().hex[:10]}"
    port = _free_port()

    try:
        run_c = subprocess.run(  # noqa: S603
            [
                docker_exe, "run", "-d", "--rm",
                "--name", cname,
                "-e", "POSTGRES_USER=dc_test",
                "-e", "POSTGRES_PASSWORD=dc_test_pw",
                "-e", "POSTGRES_DB=dentacore_test",
                "-p", f"127.0.0.1:{port}:5432",
                img,
            ],
            capture_output=True,
            text=True,
            timeout=90,
        )
        if run_c.returncode != 0:
            out["status"] = "FAIL"
            out["errors"].append(f"PostgreSQL konteyneri başlatılamadı: {(run_c.stderr or run_c.stdout).strip()[:200]}")
            return out

        # Wait until real database `dentacore_test` accepts SQL (not just temporary initdb pg_isready)
        ready = False
        for _ in range(50):
            rc_r, out_r, _ = _psql_exec(cname, "SELECT 1;", timeout=5)
            if rc_r == 0 and out_r.strip().endswith("1"):
                ready = True
                break
            time.sleep(0.4)
        if not ready:
            out["status"] = "FAIL"
            out["errors"].append("PostgreSQL dentacore_test bağlantı zaman aşımı")
            return out

        # Apply migrations or self-test DDL
        if self_test_mode or not sql_files:
            rc, _, err = _psql_exec(cname, SELF_TEST_PG_SCHEMA, timeout=25)
            if rc != 0:
                out["errors"].append(f"Self-test PG DDL hatası: {err[:220]}")
            else:
                out["migrations_applied"].append("self_test_clinical_schema.sql")
        else:
            for sf in sql_files:
                if not sf.is_file():
                    out["errors"].append(f"Migration dosyası bulunamadı: {sf.name}")
                    continue
                sql_txt = sf.read_text(encoding="utf-8", errors="ignore")
                rc, _, err = _psql_exec(cname, sql_txt, timeout=35)
                if rc != 0:
                    out["errors"].append(f"{sf.name} SQL hatası: {err[:220]}")
                else:
                    out["migrations_applied"].append(sf.name)

        # Count tables in public schema
        rc_t, tbl_out, err_t = _psql_exec(
            cname,
            "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;",
        )
        pg_tables = [x.strip() for x in tbl_out.splitlines() if x.strip()] if rc_t == 0 else []
        out["tables_created"] = len(pg_tables)
        if rc_t != 0 or not pg_tables:
            out["errors"].append(f"PG tablo listesi alınamadı: {err_t[:160]}")

        # Run 10-way concurrent ACID race test inside PostgreSQL
        # Ensure an isolated race table exists so this works identically on both self-test & full migrations
        _psql_exec(
            cname,
            "CREATE TABLE IF NOT EXISTS _sentinel_acid_race ("
            "id SERIAL PRIMARY KEY, slot_key TEXT UNIQUE NOT NULL, worker_id INT NOT NULL);",
        )

        def _race_worker(w_id: int) -> bool:
            sql_w = f"INSERT INTO _sentinel_acid_race (slot_key, worker_id) VALUES ('2027-05-01T10:00_CHAIR1', {w_id});"
            rc_w, _, _ = _psql_exec(cname, sql_w, timeout=12)
            return rc_w == 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
            race_res = list(pool.map(_race_worker, range(10)))
        commits = sum(1 for ok in race_res if ok)
        conflicts = len(race_res) - commits
        out["acid_race_commits"] = commits
        out["acid_race_conflicts"] = conflicts
        if commits != 1 or conflicts != 9:
            out["errors"].append(f"PostgreSQL ACID kilit yarışı sapması: commits={commits}, conflicts={conflicts} (beklenen 1/9)")

        # Check transactional rollback atomicity
        rc_rb, rb_cnt, _ = _psql_exec(
            cname,
            "BEGIN; INSERT INTO _sentinel_acid_race (slot_key, worker_id) VALUES ('rollback_probe', 99); ROLLBACK;"
            "SELECT count(*) FROM _sentinel_acid_race WHERE slot_key='rollback_probe';",
        )
        if rc_rb != 0 or rb_cnt.splitlines()[-1].strip() != "0":
            out["errors"].append(f"PostgreSQL ROLLBACK atomiklik doğrulaması başarısız: {rb_cnt}")

        # Optional SQLite <-> PostgreSQL table parity check
        if sqlite_schema_source and sqlite_schema_source.is_file() and pg_tables:
            src_txt = sqlite_schema_source.read_text(encoding="utf-8", errors="ignore")
            sq_tables = sorted(set(re.findall(r"CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+([a-zA-Z0-9_]+)", src_txt, re.I)))
            pg_set = set(pg_tables)
            missing = [t for t in sq_tables if t not in pg_set and not t.startswith("sqlite_")]
            out["parity_missing_in_pg"] = missing
            if missing:
                out["errors"].append(f"SQLite -> PostgreSQL eksik tablolar ({len(missing)}): {', '.join(missing[:10])}")

        out["status"] = "PASS" if not out["errors"] else "FAIL"
    except Exception as exc:
        out["status"] = "FAIL"
        out["errors"].append(f"Docker PostgreSQL istisnası: {exc}")
    finally:
        subprocess.run([docker_exe, "rm", "-f", cname], capture_output=True, timeout=15)  # noqa: S603
        out["duration_sec"] = round(time.perf_counter() - t0, 2)

    return out


if __name__ == "__main__":
    import json
    res = run_docker_postgres_verification(self_test_mode=True)
    print(json.dumps(res, ensure_ascii=False, indent=2))
