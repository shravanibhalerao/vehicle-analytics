"""
main.py
Purpose: FastAPI backend. Reads vehicle_events from PostgreSQL and
         exposes analytics endpoints for the React dashboard.
Run:     uvicorn backend.main:app --reload --port 8000
Docs:    http://localhost:8000/docs
"""

import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from psycopg2.extras import RealDictCursor

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = FastAPI(title="Vehicle Analytics API")

# Allow the React dev server to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def query(sql, params=None):
    """Run a SELECT and return a list of dict rows (new connection each time)."""
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "vehicle_analytics"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


@app.get("/api/total")
def total_count():
    """Total number of vehicles counted."""
    rows = query("SELECT COUNT(*) AS total FROM vehicle_events")
    return {"total": rows[0]["total"]}


@app.get("/api/stats/types")
def type_stats():
    """Count per vehicle type (car, bus, truck, motorcycle)."""
    rows = query(
        "SELECT vehicle_type, COUNT(*) AS count FROM vehicle_events "
        "GROUP BY vehicle_type ORDER BY count DESC"
    )
    return rows


@app.get("/api/stats/colors")
def color_stats():
    """Count per vehicle colour."""
    rows = query(
        "SELECT vehicle_color, COUNT(*) AS count FROM vehicle_events "
        "GROUP BY vehicle_color ORDER BY count DESC"
    )
    return rows


@app.get("/api/events/recent")
def recent_events(limit: int = Query(20, ge=1, le=200)):
    """Latest crossing events."""
    rows = query(
        "SELECT id, vehicle_id, vehicle_type, vehicle_color, direction, "
        "timestamp FROM vehicle_events ORDER BY id DESC LIMIT %s",
        (limit,),
    )
    for r in rows:
        r["timestamp"] = r["timestamp"].isoformat()
    return rows


@app.get("/api/analytics/history")
def history(hours: int = Query(24, ge=1, le=720)):
    """Vehicles per hour for the last N hours (for a history chart)."""
    rows = query(
        "SELECT date_trunc('hour', timestamp) AS hour, COUNT(*) AS count "
        "FROM vehicle_events "
        "WHERE timestamp >= NOW() - (%s * INTERVAL '1 hour') "
        "GROUP BY hour ORDER BY hour",
        (hours,),
    )
    for r in rows:
        r["hour"] = r["hour"].isoformat()
    return rows