from __future__ import annotations

from fastapi import BackgroundTasks, FastAPI, HTTPException, Response

from app import db
from app.schemas import ApplicationRecord, ApplyRequest, WorkflowState
from app.settings import settings
from app.workflow import DomainWorkflow

app = FastAPI(title=settings.app_name, version=settings.app_version)
workflow = DomainWorkflow()


@app.on_event("startup")
def on_startup() -> None:
    db.init_db()


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/favicon.ico")
def favicon() -> Response:
    return Response(status_code=204)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/apply", response_model=ApplicationRecord)
def apply(payload: ApplyRequest, background_tasks: BackgroundTasks) -> ApplicationRecord:
    record = db.create_application(str(payload.job_url))
    background_tasks.add_task(
        _run_workflow,
        WorkflowState(application_id=record.id, job_url=record.job_url),
    )
    return record


@app.get("/applications", response_model=list[ApplicationRecord])
def applications() -> list[ApplicationRecord]:
    return db.list_applications()


@app.get("/applications/{app_id}", response_model=ApplicationRecord)
def application_by_id(app_id: int) -> ApplicationRecord:
    try:
        return db.get_application(app_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _run_workflow(state: WorkflowState) -> None:
    try:
        workflow.run(state)
    except Exception as exc:  # noqa: BLE001
        db.update_application(state.application_id, "Failed", error_log=str(exc))
