from pydantic import BaseModel


class InquiryRequest(BaseModel):
    inquiry_text: str
    company: str = ""
    last_name: str = ""
    first_name: str = ""
    title: str = ""
    email: str = ""


class InquiryResponse(BaseModel):
    should_register: bool
    reason: str
