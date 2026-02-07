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
