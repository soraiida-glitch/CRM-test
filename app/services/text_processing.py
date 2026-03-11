import base64
import re
from datetime import UTC, datetime


def decode_base64_text(encoded_text: str) -> str:
    try:
        return base64.b64decode(encoded_text).decode("utf-8")
    except Exception:
        return ""


def extract_email(text: str) -> str | None:
    match = re.search(r"[\w.+-]+@[\w.-]+\.\w+", text)
    return match.group(0) if match else None


def extract_website(text: str) -> str | None:
    match = re.search(r"https?://[^\s]+|www\.[^\s]+", text)
    return match.group(0) if match else None


def extract_phone_candidates(text: str) -> list[str]:
    return re.findall(r"(?:\+?\d[\d\-() ]{8,}\d)", text)


def normalize_phone_number(value: str | None) -> str | None:
    if not value:
        return None
    digits = re.sub(r"\D", "", value)
    return digits or None


def extract_postal_code(text: str) -> str | None:
    match = re.search(r"\b\d{3}-?\d{4}\b", text)
    return re.sub(r"\D", "", match.group(0)) if match else None


def split_full_name(full_name: str) -> tuple[str | None, str | None]:
    parts = full_name.split()
    if len(parts) >= 2:
        return parts[-1], parts[0]
    return None, None


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
