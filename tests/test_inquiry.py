def test_inquiry_judge_detects_buying_intent(client, auth_headers):
    res = client.post(
        "/inquiry/judge",
        headers=auth_headers,
        json={
            "inquiry_text": "We are evaluating implementation and pricing for your AI tool.",
            "company": "Sample Corp",
            "last_name": "Yamada",
            "first_name": "Taro",
            "title": "Sales Director",
            "email": "yamada@example.com",
        },
    )

    assert res.status_code == 200
    body = res.json()
    assert body["should_register"] is True
    assert "購買意図" in body["reason"] or "導入" in body["reason"]
