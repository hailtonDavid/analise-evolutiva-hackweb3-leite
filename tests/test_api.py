from backend.app import app


def test_health_endpoint():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_create_evidence_flow():
    client = app.test_client()
    sample_response = client.post("/api/samples/simulate", json={"scenario": "normal", "seed": 123})
    assert sample_response.status_code == 200

    evidence_response = client.post("/api/evidence", json=sample_response.get_json())
    assert evidence_response.status_code == 200
    payload = evidence_response.get_json()

    assert "evidence" in payload
    assert "web3_registration" in payload
    assert len(payload["evidence"]["evidence_hash"]) == 64

    verify_response = client.get(f"/api/verify/{payload['evidence']['evidence_hash']}")
    assert verify_response.status_code == 200
    assert verify_response.get_json()["valid"] is True
