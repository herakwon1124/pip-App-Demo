#!/usr/bin/env python3
"""Create schema tables and load class_dataset.csv into Railway Postgres."""

from __future__ import annotations

import csv
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "data" / "class_dataset.csv"
SCHEMA_PATH = ROOT / "schema.sql"
TABLES = (
    "students",
    "tools",
    "student_tools",
    "availability",
    "student_availability",
)


def split_semicolon_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(";") if part.strip()]


def clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    if not text or text == "#NAME?":
        return None
    return text


def connect():
    load_dotenv(ROOT / ".env")
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is missing. Add it to .env (public Railway URL).")
    if "railway.internal" in database_url:
        raise SystemExit(
            "DATABASE_URL looks like Railway's private host. Use DATABASE_PUBLIC_URL locally."
        )
    if "sslmode=" not in database_url:
        joiner = "&" if "?" in database_url else "?"
        database_url = f"{database_url}{joiner}sslmode=require"
    return psycopg2.connect(database_url)


def get_or_create_lookup(cur, table: str, name: str) -> int:
    cur.execute(f"SELECT id FROM {table} WHERE name = %s", (name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(f"INSERT INTO {table} (name) VALUES (%s) RETURNING id", (name,))
    return cur.fetchone()[0]


def main() -> None:
    schema_sql = SCHEMA_PATH.read_text()

    with CSV_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    conn = connect()
    try:
        with conn:
            with conn.cursor() as cur:
                for table in reversed(TABLES):
                    cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                cur.execute(schema_sql)

                for row in rows:
                    cur.execute(
                        """
                        INSERT INTO students (
                            netid,
                            name,
                            school_year,
                            intro_programming,
                            skill_programming,
                            skill_data_stats,
                            skill_frontend_design,
                            skill_business_pitch,
                            working_style,
                            interests,
                            semester_goal,
                            submitted_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING student_id
                        """,
                        (
                            row["netid"].strip(),
                            row["name"].strip(),
                            row["school_year"].strip(),
                            row["intro_programming"].strip(),
                            int(row["skill_programming"]),
                            int(row["skill_data_stats"]),
                            int(row["skill_frontend_design"]),
                            int(row["skill_business_pitch"]),
                            clean_optional_text(row.get("working_style")),
                            clean_optional_text(row.get("interests")),
                            clean_optional_text(row.get("semester_goal")),
                            row["submitted_at"].strip(),
                        ),
                    )
                    student_id = cur.fetchone()[0]

                    for tool_name in split_semicolon_list(row.get("tools")):
                        tool_id = get_or_create_lookup(cur, "tools", tool_name)
                        cur.execute(
                            """
                            INSERT INTO student_tools (student_id, tool_id)
                            VALUES (%s, %s)
                            ON CONFLICT DO NOTHING
                            """,
                            (student_id, tool_id),
                        )

                    for slot_name in split_semicolon_list(row.get("availability")):
                        availability_id = get_or_create_lookup(cur, "availability", slot_name)
                        cur.execute(
                            """
                            INSERT INTO student_availability (student_id, availability_id)
                            VALUES (%s, %s)
                            ON CONFLICT DO NOTHING
                            """,
                            (student_id, availability_id),
                        )

                print(f"Loaded {len(rows)} CSV rows.")
                print("Table row counts:")
                for table in TABLES:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    print(f"  {table}: {cur.fetchone()[0]}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
