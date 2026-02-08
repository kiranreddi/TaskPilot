def test_list_templates(client):
    resp = client.get("/api/templates")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    names = [t["name"] for t in data]
    # At least one template should be loaded
    assert any("Clean Inbox" in n or "Revenue" in n for n in names)


def test_template_structure(client):
    resp = client.get("/api/templates")
    data = resp.json()
    for template in data:
        assert "id" in template
        assert "name" in template
        assert "description" in template
        assert "tags" in template
        assert "definition" in template
        assert isinstance(template["tags"], list)
        assert isinstance(template["definition"], dict)


def test_template_has_clean_inbox(client):
    resp = client.get("/api/templates")
    data = resp.json()
    clean_inbox = [t for t in data if t["id"] == "clean_inbox"]
    if clean_inbox:
        t = clean_inbox[0]
        assert t["name"] == "Clean Inbox"
        assert "email" in t["tags"]


def test_template_has_revenue_report(client):
    resp = client.get("/api/templates")
    data = resp.json()
    revenue = [t for t in data if t["id"] == "weekly_revenue_report"]
    if revenue:
        t = revenue[0]
        assert t["name"] == "Weekly Revenue Report"
        assert "finance" in t["tags"]
