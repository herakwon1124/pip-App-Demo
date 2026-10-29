#!/usr/bin/env python3
"""Run a small set of queries against the loaded class dataset."""

from __future__ import annotations

import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

ROOT = Path(__file__).resolve().parent

QUERIES = [
    (
        "Student count (should match CSV row count)",
        "SELECT count(*) AS n_students FROM students;",
    ),
    (
        "Sample names and school years",
        "SELECT name, school_year FROM students ORDER BY student_id LIMIT 5;",
    ),
    (
        "Students per tool",
        """
        SELECT t.name, COUNT(*) AS n_students
        FROM student_tools st
        JOIN tools t ON st.tool_id = t.id
        GROUP BY t.name
        ORDER BY n_students DESC;
        """,
    ),
]


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


def main() -> None:
    conn = connect()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            for title, sql in QUERIES:
                print(f"\n=== {title} ===")
                cur.execute(sql)
                rows = cur.fetchall()
                if not rows:
                    print("(no rows)")
                    continue
                for row in rows:
                    print(dict(row))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
