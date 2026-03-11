from typing import Optional

from pydantic import BaseModel


class VoiceLeadRequest(BaseModel):
    audio_base64: str
    mime_type: str
    filename: str


class VoiceLeadResponse(BaseModel):
    company: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile_phone: Optional[str] = None
    description: str
    raw_text: str
    request_id: str
    received_at: str
