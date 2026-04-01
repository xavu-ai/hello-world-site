"""Contributor auth router with register, login, logout endpoints."""
from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID, uuid4

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.auth import Contributor
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    RegisterRequest,
    RegisterResponse,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(user_id: UUID, secret_key: str, expires_delta: timedelta = timedelta(hours=24)) -> str:
    """Create a JWT-like access token (simplified for MVP)."""
    import base64
    import json
    
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": str(user_id),
        "exp": expire.isoformat(),
        "iat": datetime.now(timezone.utc).isoformat(),
    }
    payload_json = json.dumps(payload)
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode()
    
    # Simple signature (in production use proper JWT)
    signature_input = f"{user_id}:{expire.isoformat()}:{secret_key}"
    signature = base64.urlsafe_b64encode(signature_input.encode()).decode()[:32]
    
    return f"{payload_b64}.{signature}"


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RegisterResponse:
    """Register a new contributor."""
    # Check if email already exists
    query = select(Contributor).where(Contributor.email == request.email)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "Email already registered"},
        )
    
    # Create new contributor
    hashed = hash_password(request.password)
    contributor = Contributor(
        id=uuid4(),
        email=request.email,
        hashed_password=hashed,
        created_at=datetime.now(timezone.utc),
    )
    db.add(contributor)
    await db.commit()
    await db.refresh(contributor)
    
    return RegisterResponse(id=str(contributor.id), email=contributor.email)


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LoginResponse:
    """Login and receive an access token."""
    from app.config import settings
    
    query = select(Contributor).where(Contributor.email == request.email)
    result = await db.execute(query)
    contributor = result.scalar_one_or_none()
    
    if contributor is None or not verify_password(request.password, contributor.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Invalid credentials"},
        )
    
    token = create_access_token(contributor.id, settings.SECRET_KEY)
    
    return LoginResponse(token=token, expires_in=86400)


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current_user: Annotated[str, Depends(get_current_user)],
) -> LogoutResponse:
    """Logout the current user (client should discard token)."""
    return LogoutResponse(message="Logged out")
