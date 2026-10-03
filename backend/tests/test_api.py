from fastapi.testclient import TestClient

from database import init_db
from main import app


def test_health_and_demo_flow(tmp_path, monkeypatch):
    init_db()
    client = TestClient(app)

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["ok"] is True

    created = client.post(
        "/demo/run",
        json={"applicant_name": "Anand K. Patel", "year": 2026},
    )
    assert created.status_code == 200
    form_id = created.json()["id"]

    listed = client.get("/forms")
    assert listed.status_code == 200
    assert any(item["id"] == form_id for item in listed.json())
