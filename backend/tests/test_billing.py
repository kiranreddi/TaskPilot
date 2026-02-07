def test_stripe_webhook(client):
    resp = client.post("/api/billing/webhook", content=b'{"type": "checkout.session.completed"}')
    assert resp.status_code == 200
    assert resp.json()["received"] is True


def test_stripe_webhook_empty_body(client):
    resp = client.post("/api/billing/webhook", content=b"")
    assert resp.status_code == 200
    assert resp.json()["received"] is True
