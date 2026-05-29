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


def test_full_process_endpoint():
    client = app.test_client()
    response = client.post("/api/simulator/full-process", json={"scenario": "feed_risk", "seed": 44})
    assert response.status_code == 200
    payload = response.get_json()
    assert "soil" in payload
    assert "feed" in payload
    assert "water" in payload
    assert "milk_sample" in payload


def test_full_process_evidence_flow():
    client = app.test_client()
    response = client.post("/api/evidence/full-process", json={"scenario": "integrated_risk", "seed": 99})
    assert response.status_code == 200
    payload = response.get_json()
    assert len(payload["evidence"]["evidence_hash"]) == 64
    assert payload["evidence"]["chain_process"]["milk_sample"]["spectrometer_capture"]["channels"]


def test_simulator_page_available():
    client = app.test_client()
    response = client.get("/simulador")
    assert response.status_code == 200
    assert "Simulador da Análise Evolutiva Web3" in response.get_data(as_text=True)


def test_spectrometer_session_endpoint():
    client = app.test_client()
    response = client.post("/api/spectrometer/session", json={"scenario": "normal", "seed": 12})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["equipment"]["equipment_id"].startswith("AE-SPEC")
    assert len(payload["sample_cycles"]) == 4
    assert payload["sample_cycles"][-1]["kind"] == "milk"
    assert payload["sample_cycles"][-1]["led_sweep"]


def test_spectrometer_live_sequence_endpoint():
    client = app.test_client()
    response = client.post("/api/spectrometer/live-sequence", json={"scenario": "normal", "seed": 12})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["session_id"].startswith("AE-SPEC-SESSION")
    assert payload["live_sequence"]
    assert any(event["phase"] == "CHANNEL_CAPTURE" for event in payload["live_sequence"])


def test_investor_impact_endpoint():
    client = app.test_client()
    response = client.post("/api/investor/impact", json={"scenario": "normal", "monthly_liters": 100000})
    assert response.status_code == 200
    data = response.get_json()
    assert data["client_value_simulation"]["monthly_liters"] == 100000
    assert "business_model_simulation" in data
    assert "investment_thesis" in data

def test_investor_page():
    client = app.test_client()
    response = client.get("/investidor")
    assert response.status_code == 200
    assert b"Vis" in response.data
