from fastapi import APIRouter, Depends

from app.dependencies import verify_token
from app.schemas.inquiry import InquiryRequest, InquiryResponse
from app.services.openai_service import get_openai_service

router = APIRouter(dependencies=[Depends(verify_token)])


@router.post("/judge", response_model=InquiryResponse)
async def judge_inquiry(payload: InquiryRequest) -> InquiryResponse:
    result = await get_openai_service().judge_inquiry(payload.model_dump())
    return InquiryResponse(**result)
