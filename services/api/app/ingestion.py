from .models import IngestResult, TraceBatch
from .redaction import redact_attributes
from .storage import TraceStore


class TraceIngestor:
    def __init__(self, store: TraceStore):
        self.store = store

    def ingest(self, batch: TraceBatch) -> IngestResult:
        accepted = 0
        duplicates = 0
        for event in batch.events:
            safe_event = event.model_copy(
                update={"attributes": redact_attributes(event.attributes)}
            )
            if self.store.insert(safe_event):
                accepted += 1
            else:
                duplicates += 1
        return IngestResult(accepted=accepted, duplicates=duplicates)

