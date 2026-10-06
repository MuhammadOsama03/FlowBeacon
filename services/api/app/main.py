from typing import Annotated
from pathlib import Path as FilePath

from fastapi import Depends, FastAPI, HTTPException, Path, Query, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import __version__
from .auth import require_ingestion_key
from .dependencies import get_ingestor, get_store
from .analytics import calculate_metrics, summarize_run
from .alerts import RunAlert, detect_alerts
from .ingestion import TraceIngestor
from .evaluation import EvaluationPolicy, EvaluationResult, evaluate_run
from .models import IngestResult, RunMetrics, RunPage, RunTrace, TraceBatch, TraceStatus
from .otlp import translate_otlp
from .otlp_models import OtlpExportRequest
from .storage import TraceStore


app = FastAPI(
    title="FlowBeacon API",
    version=__version__,
    description="Secure ingestion and exploration of AI-agent traces.",
)

WEB_ROOT = FilePath(__file__).resolve().parents[2] / "web"
app.mount("/assets", StaticFiles(directory=WEB_ROOT), name="assets")


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(WEB_ROOT / "index.html")


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


@app.post("/v1/otlp/v1/traces", response_model=IngestResult,
          status_code=status.HTTP_202_ACCEPTED)
def ingest_otlp_traces(
    request: OtlpExportRequest,
    _: None = Depends(require_ingestion_key),
    ingestor: TraceIngestor = Depends(get_ingestor),
) -> IngestResult:
    return ingestor.ingest(translate_otlp(request))


RunIdentifier = Annotated[
    str,
    Path(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$"),
]


@app.get("/v1/runs", response_model=RunPage)
def list_runs(
    status_filter: Annotated[TraceStatus | None, Query(alias="status")] = None,
    search: Annotated[str | None, Query(min_length=1, max_length=128)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    store: TraceStore = Depends(get_store),
) -> RunPage:
    run_ids, total = store.list_run_ids(status=status_filter, search=search,
        limit=limit, offset=offset)
    return RunPage(items=[summarize_run(store.get_run(run_id)) for run_id in run_ids],
        total=total, limit=limit, offset=offset)


@app.get("/v1/runs/{run_id}", response_model=RunTrace)
def get_run(
    run_id: RunIdentifier,
    store: TraceStore = Depends(get_store),
) -> RunTrace:
    events = store.get_run(run_id)
    if not events:
        raise HTTPException(status_code=404, detail="Trace run not found")
    return RunTrace(run_id=run_id, events=events)


@app.get("/v1/runs/{run_id}/metrics", response_model=RunMetrics)
def get_run_metrics(run_id: RunIdentifier, store: TraceStore = Depends(get_store)) -> RunMetrics:
    events = store.get_run(run_id)
    if not events:
        raise HTTPException(status_code=404, detail="Trace run not found")
    return calculate_metrics(events)


@app.post("/v1/runs/{run_id}/evaluate", response_model=EvaluationResult)
def evaluate_trace_run(
    run_id: RunIdentifier,
    policy: EvaluationPolicy,
    store: TraceStore = Depends(get_store),
) -> EvaluationResult:
    events = store.get_run(run_id)
    if not events:
        raise HTTPException(status_code=404, detail="Trace run not found")
    return evaluate_run(events, policy)


@app.post("/v1/runs/{run_id}/alerts", response_model=list[RunAlert])
def preview_run_alerts(run_id: RunIdentifier, policy: EvaluationPolicy,
                       store: TraceStore = Depends(get_store)) -> list[RunAlert]:
    events = store.get_run(run_id)
    if not events:
        raise HTTPException(status_code=404, detail="Trace run not found")
    return detect_alerts(events, policy)
