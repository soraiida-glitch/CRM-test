from fastapi import APIRouter, Depends

from app.dependencies import verify_token

router = APIRouter(dependencies=[Depends(verify_token)])


@router.post("/embed")
def embed_case() -> dict[str, str]:
    return {"status": "stub", "message": "Implement vector store ingestion."}


@router.post("/advice")
def suggest_next_action() -> dict[str, str]:
    return {"status": "stub", "message": "Implement retrieval-augmented suggestions."}
