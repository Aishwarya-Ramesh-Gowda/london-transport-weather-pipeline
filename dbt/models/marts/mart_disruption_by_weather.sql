select
    c.weather_category,
    count(*)                                              as line_hours_observed,
    count(*) filter (where f.is_disrupted)                as line_hours_disrupted,
    round(100.0 * count(*) filter (where f.is_disrupted)
          / count(*), 2)                                  as disruption_rate_pct
from {{ ref('fct_line_status_hourly') }} f
join {{ ref('dim_weather_condition') }} c using (weather_code)
group by c.weather_category
order by disruption_rate_pct desc