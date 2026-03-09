from fastapi import APIRouter, Depends

from app.dependencies import verify_token

router = APIRouter(dependencies=[Depends(verify_token)])


@router.post("/extract")
def extract_voice() -> dict[str, str]:
    return {"status": "stub", "message": "Implement voice extraction pipeline."}
