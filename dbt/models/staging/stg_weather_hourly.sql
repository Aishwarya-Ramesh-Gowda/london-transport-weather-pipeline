select
    observation_time,
    temperature_c,
    precipitation_mm,
    wind_speed_kmh,
    weather_code,
    precipitation_mm > 0 as is_raining,
    ingested_at
from {{ source('raw', 'weather_hourly') }}