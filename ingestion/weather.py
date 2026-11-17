from datetime import UTC, datetime

import requests

from ingestion.db import get_conn

URL = "https://api.open-meteo.com/v1/forecast"
PARAMS = {
    "latitude": 51.5074,
    "longitude": -0.1278,
    "hourly": "temperature_2m,precipitation,wind_speed_10m,weather_code",
    "past_days": 2,
    "forecast_days": 1,
    "timezone": "UTC",
}


def fetch_weather():
    resp = requests.get(URL, params=PARAMS, timeout=30)
    resp.raise_for_status()
    return resp.json()["hourly"]


def load(hourly):
    sql = """
        INSERT INTO raw.weather_hourly
            (observation_time, temperature_c, precipitation_mm, wind_speed_kmh, weather_code)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (observation_time) DO UPDATE SET
            temperature_c = EXCLUDED.temperature_c,
            precipitation_mm = EXCLUDED.precipitation_mm,
            wind_speed_kmh = EXCLUDED.wind_speed_kmh,
            weather_code = EXCLUDED.weather_code,
            ingested_at = now();
    """
    rows = zip(
        hourly["time"],
        hourly["temperature_2m"],
        hourly["precipitation"],
        hourly["wind_speed_10m"],
        hourly["weather_code"],
    )
    count = 0
    with get_conn() as conn, conn.cursor() as cur:
        for t, temp, rain, wind, code in rows:
            ts = datetime.fromisoformat(t).replace(tzinfo=UTC)
            cur.execute(sql, (ts, temp, rain, wind, code))
            count += 1
    return count


def run():
    n = load(fetch_weather())
    print(f"Weather: loaded {n} hourly rows")


if __name__ == "__main__":
    run()