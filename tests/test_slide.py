def test_slide_generation_returns_case_type_and_sections(client, auth_headers):
    payload = {
        "opportunity_id": "006...",
        "name": "Sample Corp AI email automation",
        "issues": "Response time is taking 24 hours",
        "strategy": "AI-generated email drafting",
        "description": "Sales team of 20 uses Outlook",
        "close_date": "2026-06-30",
        "amount": 3000000,
    }

    res = client.post("/slide/generate-content", headers=auth_headers, json=payload)

    assert res.status_code == 200
    body = res.json()
    assert body["case_type"] == 2
    assert body["issues"]["issue_1"]
    assert len(body["questions"]["needs_and_issues"]) == 2
