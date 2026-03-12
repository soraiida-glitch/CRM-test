# salesforce-ai-service

Salesforce AI automation backend API for Cloud Run. n8n remains the trigger and output layer, while this service owns AI, scoring, vector search, and data transformation logic.

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

Use `.env` locally. In production, the application reads secret values from Google Secret Manager when `ENVIRONMENT=production`.

```env
OPENAI_API_KEY=
SALESFORCE_USERNAME=
SALESFORCE_PASSWORD=
SALESFORCE_SECURITY_TOKEN=
SALESFORCE_DOMAIN=login
API_SECRET_TOKEN=
LOG_LEVEL=INFO
ENVIRONMENT=local
GCP_PROJECT_ID=
OPENAI_API_KEY_SECRET_NAME=OPENAI_API_KEY
SALESFORCE_USERNAME_SECRET_NAME=SALESFORCE_USERNAME
SALESFORCE_PASSWORD_SECRET_NAME=SALESFORCE_PASSWORD
SALESFORCE_SECURITY_TOKEN_SECRET_NAME=SALESFORCE_SECURITY_TOKEN
API_SECRET_TOKEN_SECRET_NAME=API_SECRET_TOKEN
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

## Deployment

Pushes to `main` trigger GitHub Actions deployment to Cloud Run after test success.

The deploy job uses Workload Identity Federation, pushes an image to Docker Hub, and deploys Cloud Run in `asia-northeast1`.

Before the first deploy, prepare the GCP side:

```text
Enable APIs:
- run.googleapis.com
- secretmanager.googleapis.com
- iamcredentials.googleapis.com

Grant the deploy service account:
- roles/run.admin
- roles/iam.serviceAccountUser

Grant the Cloud Run runtime service account:
- roles/secretmanager.secretAccessor
```

## Required GitHub Secrets

```text
GCP_PROJECT_ID
GCP_WORKLOAD_IDENTITY_PROVIDER
GCP_SERVICE_ACCOUNT_EMAIL
GCP_RUNTIME_SERVICE_ACCOUNT_EMAIL
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

## Required Google Secret Manager Secrets

```text
API_SECRET_TOKEN
OPENAI_API_KEY
SALESFORCE_USERNAME
SALESFORCE_PASSWORD
SALESFORCE_SECURITY_TOKEN
```
