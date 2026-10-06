import csv
import io

from .models import TraceEvent


def export_ndjson(events: list[TraceEvent]) -> str:
    return "".join(event.model_dump_json() + "\n" for event in events)


def export_csv(events: list[TraceEvent]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=["event_id", "run_id", "span_id",
        "parent_span_id", "timestamp", "event_type", "status", "duration_ms"])
    writer.writeheader()
    for event in events:
        writer.writerow({key: value for key, value in event.model_dump(mode="json").items()
                         if key in writer.fieldnames})
    return output.getvalue()
