def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_unauthorized(client):
    res = client.post("/inquiry/judge", json={"inquiry_text": "Need a demo"})
    assert res.status_code == 403
