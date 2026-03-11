import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends

from app.dependencies import verify_token
from app.schemas.slide import (
    SlideInsight,
    SlideIssues,
    SlideMeta,
    SlideQuestions,
    SlideRequest,
    SlideResponse,
    SlideUseCases,
)
from app.services.openai_service import get_openai_service

router = APIRouter(dependencies=[Depends(verify_token)])


@router.post("/generate-content", response_model=SlideResponse)
async def generate_slide_content(payload: SlideRequest) -> SlideResponse:
    service = get_openai_service()
    issues, use_cases, questions, insight, case_type = await asyncio.gather(
        _build_issues(service, payload),
        _build_use_cases(service, payload),
        _build_questions(service, payload),
        _build_insight(service, payload),
        _classify_case_type(service, payload),
    )
    return SlideResponse(
        meta=SlideMeta(
            company_name=payload.name.split()[0],
            run_month=datetime.now().strftime("%B %Y"),
        ),
        issues=issues,
        use_cases=use_cases,
        questions=questions,
        insight=insight,
        case_type=case_type,
    )


async def _build_issues(service, payload: SlideRequest) -> SlideIssues:
    return SlideIssues(**await service.generate_slide_section("issues", payload.model_dump()))


async def _build_use_cases(service, payload: SlideRequest) -> SlideUseCases:
    return SlideUseCases(**await service.generate_slide_section("use_cases", payload.model_dump()))


async def _build_questions(service, payload: SlideRequest) -> SlideQuestions:
    return SlideQuestions(**await service.generate_slide_section("questions", payload.model_dump()))


async def _build_insight(service, payload: SlideRequest) -> SlideInsight:
    return SlideInsight(**await service.generate_slide_section("insight", payload.model_dump()))


async def _classify_case_type(service, payload: SlideRequest) -> int:
    return await service.generate_slide_section("case_type", payload.model_dump())
