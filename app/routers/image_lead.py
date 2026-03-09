from fastapi import APIRouter, Depends

from app.dependencies import verify_token

router = APIRouter(dependencies=[Depends(verify_token)])


@router.post("/analyze")
def analyze_image() -> dict[str, str]:
    return {"status": "stub", "message": "Implement business card OCR and enrichment."}
