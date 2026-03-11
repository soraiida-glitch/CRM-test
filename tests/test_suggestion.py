def test_embed_and_advice_flow(client, auth_headers):
    embed_res = client.post(
        "/suggestion/embed",
        headers=auth_headers,
        json={
            "cases": [
                {
                    "opportunity_id": "006-1",
                    "amount": 3000000,
                    "income": 8000000,
                    "family": "married",
                    "log": "Three meetings. Trust and competitor handling closed the deal.",
                }
            ]
        },
    )
    assert embed_res.status_code == 200
    assert embed_res.json()["stored_count"] == 1

    advice_res = client.post(
        "/suggestion/advice",
        headers=auth_headers,
        json={
            "opportunity": {
                "name": "Sample Opportunity",
                "stage": "Proposal",
                "amount": 3000000,
                "probability": 60,
                "close_date": "2026-04-30",
                "family": "married",
                "income": 7000000,
                "age": 42,
                "cause": "exhibition",
                "rival": True,
                "description": "Comparing with two competitors",
            }
        },
    )

    assert advice_res.status_code == 200
    body = advice_res.json()
    assert body["similar_cases_count"] >= 1
    assert "参考にした過去の成功事例" in body["advice"]
