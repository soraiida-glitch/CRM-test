from typing import Optional

from pydantic import BaseModel


class ImageLeadRequest(BaseModel):
    image_base64: str
    mime_type: str


class ImageLeadResponse(BaseModel):
    company: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile_phone: Optional[str] = None
    fax: Optional[str] = None
    website: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    raw_text: str
