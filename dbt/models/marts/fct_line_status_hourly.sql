select
    s.line_id,
    s.snapshot_hour,
    s.status_severity,
    s.status_description,
    s.is_disrupted,
    s.disruption_reason,
    w.weather_code,
    w.temperature_c,
    w.precipitation_mm,
    w.wind_speed_kmh,
    w.is_raining
from {{ ref('stg_tfl_line_status') }} s
left join {{ ref('stg_weather_hourly') }} w
    on s.snapshot_hour = w.observation_time