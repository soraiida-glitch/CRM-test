from fastapi import FastAPI

from app.routers import image_lead, inquiry, sales_eval, slide, suggestion, voice_lead

app = FastAPI(title="Salesforce AI Service", version="1.0.0")

app.include_router(inquiry.router, prefix="/inquiry", tags=["inquiry"])
app.include_router(image_lead.router, prefix="/image-lead", tags=["image-lead"])
app.include_router(voice_lead.router, prefix="/voice-lead", tags=["voice-lead"])
app.include_router(sales_eval.router, prefix="/sales-eval", tags=["sales-eval"])
app.include_router(suggestion.router, prefix="/suggestion", tags=["suggestion"])
app.include_router(slide.router, prefix="/slide", tags=["slide"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "1.0.0"}
