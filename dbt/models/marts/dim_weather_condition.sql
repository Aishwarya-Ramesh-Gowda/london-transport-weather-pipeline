select
    code as weather_code,
    case
        when code = 0                then 'Clear'
        when code between 1 and 3    then 'Cloudy'
        when code in (45, 48)        then 'Fog'
        when code between 51 and 57  then 'Drizzle'
        when code between 61 and 67  then 'Rain'
        when code between 71 and 77  then 'Snow'
        when code between 80 and 82  then 'Showers'
        when code between 95 and 99  then 'Thunderstorm'
        else 'Other'
    end as weather_category
from generate_series(0, 99) as code