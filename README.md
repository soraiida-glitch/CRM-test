# salesforce-ai-service

Salesforce AI automation backend API for Cloud Run. n8n remains the trigger and output layer, while this service owns the AI, scoring, and data transformation logic.

## Local setup

```bash
cp .env.example .env
# fill in your local secrets

python -m venv .venv
.venv\Scripts\pip install -r requirements-dev.txt
.venv\Scripts\uvicorn app.main:app --reload
```

## Tests

```bash
.venv\Scripts\python -m pytest tests/ -v
```

## Environment variables

Use `.env` locally. In production, this repository currently injects values from GitHub Secrets into Cloud Run environment variables directly.

```env
OPENAI_API_KEY=
SALESFORCE_USERNAME=
SALESFORCE_PASSWORD=
SALESFORCE_SECURITY_TOKEN=
SALESFORCE_DOMAIN=login
API_SECRET_TOKEN=
LOG_LEVEL=INFO
ENVIRONMENT=local
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

## GitHub Secrets

Required for Cloud Run deployment:

```text
GCP_PROJECT_ID
GCP_WORKLOAD_IDENTITY_PROVIDER
GCP_SERVICE_ACCOUNT_EMAIL
API_SECRET_TOKEN
OPENAI_API_KEY
SALESFORCE_USERNAME
SALESFORCE_PASSWORD
SALESFORCE_SECURITY_TOKEN
```

For Workload Identity Federation:

- `GCP_WORKLOAD_IDENTITY_PROVIDER`: fully qualified provider resource name
  Example: `projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github-provider`
- `GCP_SERVICE_ACCOUNT_EMAIL`: service account email used by GitHub Actions
  Example: `github-actions-deploy@your-project-id.iam.gserviceaccount.com`

Current production fallback:

- Secret Manager is not required for this workflow.
- GitHub Actions reads the repository secrets and sets them as Cloud Run environment variables during deploy.
- This is simpler to operate, but less strict than Secret Manager. Migrate later if billing and permissions become available.

## Deploy

Pushes to `main` trigger GitHub Actions deployment to Cloud Run after test success.
