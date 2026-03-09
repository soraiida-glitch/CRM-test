from fastapi import APIRouter, Depends

from app.dependencies import verify_token
from app.schemas.inquiry import InquiryRequest, InquiryResponse

router = APIRouter(dependencies=[Depends(verify_token)])


@router.post("/judge", response_model=InquiryResponse)
def judge_inquiry(payload: InquiryRequest) -> InquiryResponse:
    should_register = len(payload.inquiry_text.strip()) > 0
    reason = "Stub response. Implement inquiry qualification logic."
    return InquiryResponse(should_register=should_register, reason=reason)
