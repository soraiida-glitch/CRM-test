# salesforce-ai-service

Salesforce-integrated AI automation backend API for Cloud Run.

## Local setup

```bash
cp .env.example .env
# edit .env as needed

pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

## Tests

```bash
pytest tests/ -v
```

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | /health | Health check |
| POST | /inquiry/judge | Inquiry qualification |
| POST | /image-lead/analyze | Business card image analysis |
| POST | /voice-lead/extract | Voice note extraction |
| POST | /sales-eval/prioritize | Priority scoring |
| POST | /sales-eval/score | Sales activity evaluation |
| POST | /suggestion/embed | Store success cases |
| POST | /suggestion/advice | RAG-based advice |
| POST | /slide/generate-content | Slide content generation |

## Deploy

Pushes to `main` trigger GitHub Actions deployment to Cloud Run.
