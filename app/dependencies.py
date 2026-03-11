from fastapi import HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.request_context import request_id_var

security = HTTPBearer(auto_error=False)


def verify_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    if credentials is None or credentials.credentials != settings.api_secret_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )
    request.state.request_id = request_id_var.get()
    return credentials.credentials
