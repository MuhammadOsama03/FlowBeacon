from fastapi import Depends, FastAPI, status

from . import __version__
from .dependencies import get_ingestor
from .ingestion import TraceIngestor
from .models import IngestResult, TraceBatch


app = FastAPI(
    title="FlowBeacon API",
    version=__version__,
    description="Secure ingestion and exploration of AI-agent traces.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "flowbeacon-api", "version": __version__}


@app.post(
    "/v1/events",
    response_model=IngestResult,
    status_code=status.HTTP_202_ACCEPTED,
)
def ingest_events(
    batch: TraceBatch,
    ingestor: TraceIngestor = Depends(get_ingestor),
) -> IngestResult:
    return ingestor.ingest(batch)

