def test_get_run(client, auth_headers):
    # Create and run a workflow first
    create_resp = client.post("/api/workflows", headers=auth_headers, json={
        "name": "Test WF",
    })
    wf_id = create_resp.json()["id"]
    run_resp = client.post(f"/api/workflows/{wf_id}/run", headers=auth_headers, json={})
    run_id = run_resp.json()["id"]

    resp = client.get(f"/api/runs/{run_id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == run_id
    assert data["status"] == "SUCCEEDED"
    assert len(data["steps"]) >= 1


def test_get_run_not_found(client, auth_headers):
    resp = client.get("/api/runs/nonexistent", headers=auth_headers)
    assert resp.status_code == 404


def test_get_run_no_auth(client):
    resp = client.get("/api/runs/any-id")
    assert resp.status_code == 401


def test_cancel_run_not_found(client, auth_headers):
    resp = client.post("/api/runs/nonexistent/cancel", headers=auth_headers)
    assert resp.status_code == 404


def test_cancel_run_no_auth(client):
    resp = client.post("/api/runs/any-id/cancel")
    assert resp.status_code == 401


def test_cancel_completed_run(client, auth_headers):
    create_resp = client.post("/api/workflows", headers=auth_headers, json={
        "name": "Cancel Test WF",
    })
    wf_id = create_resp.json()["id"]
    run_resp = client.post(f"/api/workflows/{wf_id}/run", headers=auth_headers, json={})
    run_id = run_resp.json()["id"]

    resp = client.post(f"/api/runs/{run_id}/cancel", headers=auth_headers)
    assert resp.status_code == 400


def test_cancel_queued_run(client, auth_headers, db_session):
    from app import models as m
    create_resp = client.post("/api/workflows", headers=auth_headers, json={
        "name": "Cancelable WF",
    })
    wf_id = create_resp.json()["id"]
    run_resp = client.post(f"/api/workflows/{wf_id}/run", headers=auth_headers, json={})
    run_id = run_resp.json()["id"]

    # Manually set status to QUEUED so cancellation is allowed
    run = db_session.query(m.Run).filter(m.Run.id == run_id).first()
    run.status = "QUEUED"
    db_session.commit()

    resp = client.post(f"/api/runs/{run_id}/cancel", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "CANCELED"


def test_get_run_with_steps_detail(client, auth_headers):
    create_resp = client.post("/api/workflows", headers=auth_headers, json={
        "name": "Steps Detail WF",
    })
    wf_id = create_resp.json()["id"]
    run_resp = client.post(f"/api/workflows/{wf_id}/run", headers=auth_headers, json={})
    run_id = run_resp.json()["id"]

    resp = client.get(f"/api/runs/{run_id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "steps" in data
    assert len(data["steps"]) >= 1
    step = data["steps"][0]
    assert "id" in step
    assert "step_index" in step
    assert "tool" in step
    assert "status" in step


def test_run_step_outputs(client, auth_headers):
    create_resp = client.post("/api/workflows", headers=auth_headers, json={
        "name": "Step Output WF",
    })
    wf_id = create_resp.json()["id"]
    run_resp = client.post(f"/api/workflows/{wf_id}/run", headers=auth_headers, json={})
    run_id = run_resp.json()["id"]

    resp = client.get(f"/api/runs/{run_id}", headers=auth_headers)
    data = resp.json()
    for step in data["steps"]:
        assert step["status"] == "SUCCEEDED"
        assert step["output_json"] is not None
