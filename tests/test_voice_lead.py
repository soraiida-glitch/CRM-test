import base64


def test_voice_lead_extract_returns_request_metadata(client, auth_headers):
    raw_text = "\n".join(
        [
            "Sample Corp",
            "Director",
            "Taro Yamada",
            "03-1234-5678",
            "Customer wants an AI demo next week.",
        ]
    )
    payload = {
        "audio_base64": base64.b64encode(raw_text.encode("utf-8")).decode("utf-8"),
        "mime_type": "audio/m4a",
        "filename": "call_20260309.m4a",
    }

    res = client.post("/voice-lead/extract", headers=auth_headers, json=payload)

    assert res.status_code == 200
    body = res.json()
    assert body["request_id"].startswith("req_")
    assert body["phone"] == "0312345678"
    assert body["description"] == "Customer wants an AI demo next week."
