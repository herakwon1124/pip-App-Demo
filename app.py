#!/usr/bin/env python3
"""Flask backend: serve the roster page and student names from Postgres."""

from __future__ import annotations

import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory
from psycopg2.extras import RealDictCursor

ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"

load_dotenv(ROOT / ".env")

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/static")


def database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    if "sslmode=" not in url:
        joiner = "&" if "?" in url else "?"
        url = f"{url}{joiner}sslmode=require"
    return url


def fetch_students() -> list[dict]:
    conn = psycopg2.connect(database_url())
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT name, school_year
                FROM students
                ORDER BY name
                """
            )
            return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


@app.get("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.get("/api/students")
def students():
    try:
        rows = fetch_students()
    except Exception as exc:
        return jsonify({"error": "Could not load students from the database.", "detail": str(exc)}), 500
    return jsonify({"students": rows, "count": len(rows)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
