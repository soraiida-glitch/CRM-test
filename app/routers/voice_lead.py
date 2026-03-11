from fastapi import APIRouter, Depends, Request

from app.dependencies import verify_token
from app.schemas.voice_lead import VoiceLeadRequest, VoiceLeadResponse
from app.services.openai_service import get_openai_service
from app.services.text_processing import utc_now_iso

router = APIRouter(dependencies=[Depends(verify_token)])


@router.post("/extract", response_model=VoiceLeadResponse)
async def extract_voice(payload: VoiceLeadRequest, request: Request) -> VoiceLeadResponse:
    service = get_openai_service()
    raw_text = await service.transcribe_audio(payload.audio_base64, payload.filename)
    parsed = await service.extract_voice_lead(raw_text)
    return VoiceLeadResponse(
        company=parsed.company,
        first_name=parsed.first_name,
        last_name=parsed.last_name,
        title=parsed.title,
        email=parsed.email,
        phone=parsed.phone,
        mobile_phone=parsed.mobile_phone,
        description=parsed.description or payload.filename,
        raw_text=parsed.raw_text,
        request_id=request.state.request_id,
        received_at=utc_now_iso(),
    )
