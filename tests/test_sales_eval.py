def test_prioritize_sales_returns_ranked_results(client, auth_headers):
    payload = {
        "opportunities": [
            {
                "opportunity_id": "006-high",
                "owner_id": "005-owner",
                "owner_name": "Ichiro Tanaka",
                "name": "Sample AI rollout",
                "stage": "Negotiation",
                "amount": 5000000,
                "probability": 70,
                "close_date": "2026-03-20",
                "last_activity_date": "2026-03-01",
                "next_step": "",
                "decision_maker_contacted": False,
                "description": "Email automation deal",
            },
            {
                "opportunity_id": "006-low",
                "owner_id": "005-owner",
                "owner_name": "Ichiro Tanaka",
                "name": "Small renewal",
                "stage": "Prospecting",
                "amount": 100000,
                "probability": 10,
                "close_date": "2026-06-01",
                "last_activity_date": "2026-03-08",
                "next_step": "Send email",
                "decision_maker_contacted": True,
                "description": "",
            },
        ]
    }

    res = client.post("/sales-eval/prioritize", headers=auth_headers, json=payload)

    assert res.status_code == 200
    body = res.json()
    assert body["results"][0]["opportunity_id"] == "006-high"
    assert body["results"][0]["rank"] == 1


def test_score_sales_applies_penalty(client, auth_headers):
    payload = {
        "user_name": "Ichiro Tanaka",
        "recommended_actions": [
            {
                "row_number": 2,
                "opportunity_name": "Sample AI rollout",
                "action": "Call the buyer today",
                "reason": "High priority deal",
            }
        ],
        "actual_tasks": [
            {
                "task_subject": "Follow-up call",
                "opportunity_name": "Sample AI rollout",
                "priority_score": 10,
                "task_description": "Spoke with director and booked next meeting.",
                "task_status": "Completed",
            }
        ],
        "pending_tasks": [{"row_number": 1, "task_date": "2026-03-01", "mark": ""}],
    }

    res = client.post("/sales-eval/score", headers=auth_headers, json=payload)

    assert res.status_code == 200
    body = res.json()
    assert body["penalty"]["pending_count"] == 1
    assert body["penalty"]["final_score"] <= body["total_score"]
    assert body["completed_rows"][0]["mark"] == ""
    assert body["action_alignment_status"] == "達成"
