select distinct
    line_id,
    line_name
from {{ ref('stg_tfl_line_status') }}