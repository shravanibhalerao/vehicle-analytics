"""
db.py
Purpose: Save one confirmed line-crossing event into PostgreSQL.
"""

import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

# Load settings from the .env file in the project root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

_conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432"),
    dbname=os.getenv("DB_NAME", "vehicle_analytics"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", ""),
)
_conn.autocommit = True


def save_event(vehicle_id, vehicle_type, vehicle_color, direction):
    """Insert one row into vehicle_events."""
    with _conn.cursor() as cur:
        cur.execute(
            "INSERT INTO vehicle_events "
            "(vehicle_id, vehicle_type, vehicle_color, direction) "
            "VALUES (%s, %s, %s, %s)",
            (int(vehicle_id), vehicle_type, vehicle_color, direction),
        )