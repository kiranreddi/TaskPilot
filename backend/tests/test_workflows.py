def test_list_workflows_empty(client, auth_headers):
    resp = client.get("/api/workflows", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_workflows_no_auth(client):
    resp = client.get("/api/workflows")
    assert resp.status_code == 401


def test_create_workflow(client, auth_headers):
    resp = client.post("/api/workflows", headers=auth_headers, json={
        "name": "Test Workflow",
        "description": "A test workflow",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Workflow"
    assert data["status"] == "ACTIVE"


def test_create_workflow_no_auth(client):
    resp = client.post("/api/workflows", json={"name": "Test"})
    assert resp.status_code == 401


def test_create_workflow_missing_name(client, auth_headers):
    resp = client.post("/api/workflows", headers=auth_headers, json={})
    assert resp.status_code == 422


def test_create_workflow_with_definition(client, auth_headers):
    resp = client.post("/api/workflows", headers=auth_headers, json={
        "name": "Custom Workflow",
        "definition": {
            "steps": [
                {"id": "s1", "tool": "taskpilot.llm.summarize", "args": {"items_ref": "input", "style": "default"}}
            ]
        },
    })
    assert resp.status_code == 201


def test_create_workflow_invalid_definition(client, auth_headers):
    resp = client.post("/api/workflows", headers=auth_headers, json={
        "name": "Bad Workflow",
        "definition": {"steps": [{"id": "s1", "tool": "nonexistent.tool"}]},
    })
    assert resp.status_code == 422


def test_run_workflow(client, auth_headers):
    create_resp = client.post("/api/workflows", headers=auth_headers, json={
        "name": "Runnable Workflow",
    })
    wf_id = create_resp.json()["id"]

    resp = client.post(f"/api/workflows/{wf_id}/run", headers=auth_headers, json={
        "inputs": {"key": "value"},
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCEEDED"
    assert len(data["steps"]) == 1


def test_run_workflow_not_found(client, auth_headers):
    resp = client.post("/api/workflows/nonexistent/run", headers=auth_headers, json={})
    assert resp.status_code == 404


def test_run_workflow_no_auth(client):
    resp = client.post("/api/workflows/any-id/run", json={})
    assert resp.status_code == 401


def test_run_workflow_with_write_steps_no_approval(client, auth_headers):
    resp = client.post("/api/workflows", headers=auth_headers, json={
        "name": "Write Workflow",
        "definition": {
            "steps": [
                {"id": "s1", "tool": "google.gmail.label.apply", "args": {"label": "test"}}
            ]
        },
    })
    wf_id = resp.json()["id"]

    resp = client.post(f"/api/workflows/{wf_id}/run", headers=auth_headers, json={})
    assert resp.status_code == 200
    assert resp.json()["status"] == "FAILED"
    assert "approval" in resp.json()["output_summary"].lower()


def test_run_workflow_with_write_steps_with_approval(client, auth_headers):
    resp = client.post("/api/workflows", headers=auth_headers, json={
        "name": "Approved Write Workflow",
        "definition": {
            "steps": [
                {"id": "s1", "tool": "google.gmail.label.apply", "args": {"label": "test"}}
            ]
        },
    })
    wf_id = resp.json()["id"]

    resp = client.post(f"/api/workflows/{wf_id}/run", headers=auth_headers, json={
        "approval_token": "approved",
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "SUCCEEDED"


def test_list_workflows_after_create(client, auth_headers):
    client.post("/api/workflows", headers=auth_headers, json={"name": "WF1"})
    client.post("/api/workflows", headers=auth_headers, json={"name": "WF2"})
    resp = client.get("/api/workflows", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2
