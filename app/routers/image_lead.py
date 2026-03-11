from fastapi import APIRouter, Depends

from app.dependencies import verify_token
from app.schemas.image_lead import ImageLeadRequest, ImageLeadResponse
from app.services.openai_service import get_openai_service

router = APIRouter(dependencies=[Depends(verify_token)])


@router.post("/analyze", response_model=ImageLeadResponse)
async def analyze_image(payload: ImageLeadRequest) -> ImageLeadResponse:
    parsed = await get_openai_service().analyze_business_card(
        payload.image_base64, payload.mime_type
    )
    return ImageLeadResponse(**parsed.__dict__)
