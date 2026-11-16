import os
from datetime import datetime, timezone

import requests
from psycopg2.extras import Json

from ingestion.db import get_conn

URL = "https://api.tfl.gov.uk/Line/Mode/tube/Status"


def fetch_status():
    params = {}
    key = os.getenv("TFL_APP_KEY")
    if key and key != "optional":
        params["app_key"] = key
    resp = requests.get(URL, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def load(lines, snapshot_hour):
    sql = """
        INSERT INTO raw.tfl_line_status (line_id, snapshot_hour, payload)
        VALUES (%s, %s, %s)
        ON CONFLICT (line_id, snapshot_hour)
        DO UPDATE SET payload = EXCLUDED.payload, ingested_at = now();
    """
    with get_conn() as conn, conn.cursor() as cur:
        for line in lines:
            cur.execute(sql, (line["id"], snapshot_hour, Json(line)))
    return len(lines)


def run():
    snapshot_hour = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    lines = fetch_status()
    n = load(lines, snapshot_hour)
    print(f"TfL: loaded {n} lines for {snapshot_hour.isoformat()}")


if __name__ == "__main__":
    run()