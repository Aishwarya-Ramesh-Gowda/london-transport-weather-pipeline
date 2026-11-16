from datetime import datetime, timedelta

from airflow.decorators import dag, task

default_args = {
    "owner": "data-eng",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    dag_id="london_transport_weather_hourly",
    description="Hourly ingest of TfL line status and London weather into raw schema",
    schedule="@hourly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["ingestion", "tfl", "weather"],
)
def london_transport_weather():
    @task
    def ingest_tfl():
        from ingestion import tfl
        tfl.run()

    @task
    def ingest_weather():
        from ingestion import weather
        weather.run()

    # No dependency between them, so they run in parallel
    ingest_tfl()
    ingest_weather()


london_transport_weather()