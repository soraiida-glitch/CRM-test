def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
    assert "version" in res.json()
    assert "x-request-id" in res.headers


def test_unauthorized(client):
    res = client.post("/inquiry/judge", json={"inquiry_text": "Need a demo"})
    assert res.status_code == 401
    assert res.json()["request_id"]
