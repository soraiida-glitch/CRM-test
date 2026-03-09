from fastapi import APIRouter, Depends

from app.dependencies import verify_token

router = APIRouter(dependencies=[Depends(verify_token)])


@router.post("/generate-content")
def generate_slide_content() -> dict[str, str]:
    return {"status": "stub", "message": "Implement slide content generation."}
