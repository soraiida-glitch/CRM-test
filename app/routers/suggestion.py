from fastapi import APIRouter, Depends

from app.dependencies import verify_token
from app.schemas.suggestion import (
    AdviceRequest,
    AdviceResponse,
    EmbedRequest,
    EmbedResponse,
)
from app.services.openai_service import get_openai_service
from app.services.vector_store import query_similar_cases, upsert_cases

router = APIRouter(dependencies=[Depends(verify_token)])


@router.post("/embed", response_model=EmbedResponse)
def embed_case(payload: EmbedRequest) -> EmbedResponse:
    items = [
        {
            "opportunity_id": item.opportunity_id,
            "document": item.log,
            "metadata": {
                "amount": item.amount,
                "income": item.income,
                "family": item.family,
                "rival": "rival" in item.log.lower() or "competitor" in item.log.lower(),
            },
        }
        for item in payload.cases
    ]
    return EmbedResponse(stored_count=upsert_cases(items))


@router.post("/advice", response_model=AdviceResponse)
async def suggest_next_action(payload: AdviceRequest) -> AdviceResponse:
    similar_cases = query_similar_cases(
        {
            "amount": payload.opportunity.amount,
            "income": payload.opportunity.income,
            "family": payload.opportunity.family,
            "rival": payload.opportunity.rival,
        }
    )
    advice = await get_openai_service().generate_advice(
        payload.opportunity.model_dump(), similar_cases
    )
    return AdviceResponse(advice=advice, similar_cases_count=len(similar_cases))
