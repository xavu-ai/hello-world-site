"""Authentication and authorization dependencies."""
import base64
import json
from datetime import datetime, timezone
from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

security = HTTPBearer(auto_error=False)


def verify_access_token(token: str, secret_key: str) -> UUID | None:
    """Verify access token and return user_id if valid."""
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        payload_b64, signature = parts
        
        payload_json = base64.urlsafe_b64decode(payload_b64.encode()).decode()
        payload = json.loads(payload_json)
        
        user_id = UUID(payload["sub"])
        expire = datetime.fromisoformat(payload["exp"])
        
        if datetime.now(timezone.utc) > expire:
            return None
            
        # Verify signature
        signature_input = f"{user_id}:{expire.isoformat()}:{secret_key}"
        expected_sig = base64.urlsafe_b64encode(signature_input.encode()).decode()[:32]
        
        if signature != expected_sig:
            return None
            
        return user_id
    except Exception:
        return None


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
) -> str:
    """
    Authentication dependency that validates Bearer token and returns user_id.
    
    Raises HTTPException 401 if token is missing or invalid.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Authentication required"},
        )

    token = credentials.credentials
    user_id = verify_access_token(token, settings.SECRET_KEY)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Invalid or expired token"},
        )

    return str(user_id)
