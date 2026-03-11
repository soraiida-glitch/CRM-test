import base64


def test_image_lead_analyze_extracts_contact_fields(client, auth_headers):
    raw_text = "\n".join(
        [
            "Sample Corp",
            "Sales Director",
            "Taro Yamada",
            "yamada@example.com",
            "1-1-1 Marunouchi Chiyoda-ku Tokyo",
            "03-1234-5678",
            "090-1234-5678",
            "https://sample.co.jp",
        ]
    )
    payload = {
        "image_base64": base64.b64encode(raw_text.encode("utf-8")).decode("utf-8"),
        "mime_type": "image/jpeg",
    }

    res = client.post("/image-lead/analyze", headers=auth_headers, json=payload)

    assert res.status_code == 200
    body = res.json()
    assert body["company"] == "Sample Corp"
    assert body["last_name"] == "Taro"
    assert body["first_name"] == "Yamada"
    assert body["email"] == "yamada@example.com"
    assert body["phone"] == "0312345678"
