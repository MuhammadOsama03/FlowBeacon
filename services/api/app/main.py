from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path, status

from . import __version__
from .auth import require_ingestion_key
from .dependencies import get_ingestor, get_store
from .ingestion import TraceIngestor
from .models import IngestResult, RunTrace, TraceBatch
from .storage import TraceStore


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
    _: None = Depends(require_ingestion_key),
    ingestor: TraceIngestor = Depends(get_ingestor),
) -> IngestResult:
    return ingestor.ingest(batch)


RunIdentifier = Annotated[
    str,
    Path(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$"),
]


@app.get("/v1/runs/{run_id}", response_model=RunTrace)
def get_run(
    run_id: RunIdentifier,
    store: TraceStore = Depends(get_store),
) -> RunTrace:
    events = store.get_run(run_id)
    if not events:
        raise HTTPException(status_code=404, detail="Trace run not found")
    return RunTrace(run_id=run_id, events=events)
