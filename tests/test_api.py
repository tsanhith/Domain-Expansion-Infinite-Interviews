from pathlib import Path

from fastapi.testclient import TestClient

from app import db
from app.main import app


def setup_module() -> None:
    test_db = Path("data/test_applications.db")
    if test_db.exists():
        test_db.unlink()
    db.DB_PATH = test_db
    db.init_db()


def teardown_module() -> None:
    if db.DB_PATH.exists():
        db.DB_PATH.unlink()


def test_root_and_health() -> None:
    client = TestClient(app)

    root_response = client.get("/")
    assert root_response.status_code == 200
    root_body = root_response.json()
    assert root_body["status"] == "running"

    favicon_response = client.get("/favicon.ico")
    assert favicon_response.status_code == 204

    health_response = client.get("/health")
    assert health_response.status_code == 200
    assert health_response.json() == {"status": "ok"}


def test_apply_flow_completes() -> None:
    client = TestClient(app)

    response = client.post("/apply", json={"job_url": "https://example.com/job/123"})
    assert response.status_code == 200
    created = response.json()
    assert created["status"] == "Pending"

    app_id = created["id"]
    fetched = client.get(f"/applications/{app_id}")
    assert fetched.status_code == 200
    body = fetched.json()
    assert body["status"] == "Applied"
    assert body["resume_pdf_path"].endswith(f"resume_{app_id}.pdf")


def test_list_applications_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/applications")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
