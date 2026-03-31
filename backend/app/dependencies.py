"""Authentication and authorization dependencies."""
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
) -> Optional[str]:
    """
    Optional authentication dependency for future use.

    Validates Bearer token if present and returns the user identifier.
    Returns None if no token is provided (allows unauthenticated access).
    """
    if credentials is None:
        return None

    token = credentials.credentials
    # Placeholder for actual token validation logic
    # In production, this would verify the JWT or lookup the session
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Invalid authentication token"},
        )

    # For now, just return the token as the user identifier
    # Replace with actual user extraction logic (e.g., JWT decode)
    return token
