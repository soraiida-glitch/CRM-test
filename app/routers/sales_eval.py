from fastapi import APIRouter, Depends

from app.dependencies import verify_token

router = APIRouter(dependencies=[Depends(verify_token)])


@router.post("/prioritize")
def prioritize_sales() -> dict[str, str]:
    return {"status": "stub", "message": "Implement priority scoring endpoint."}


@router.post("/score")
def score_sales_activity() -> dict[str, str]:
    return {"status": "stub", "message": "Implement sales evaluation endpoint."}
