select
    line_id,
    snapshot_hour,
    payload ->> 'name'                                           as line_name,
    (payload -> 'lineStatuses' -> 0 ->> 'statusSeverity')::int   as status_severity,
    payload -> 'lineStatuses' -> 0 ->> 'statusSeverityDescription' as status_description,
    payload -> 'lineStatuses' -> 0 ->> 'reason'                  as disruption_reason,
    -- TfL severity 10 = Good Service, 18 = No Issues; anything else is a disruption
    (payload -> 'lineStatuses' -> 0 ->> 'statusSeverity')::int not in (10, 18) as is_disrupted,
    ingested_at
from {{ source('raw', 'tfl_line_status') }}