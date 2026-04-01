"""Pydantic schemas for auth endpoints."""
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Schema for registration request."""

    email: EmailStr
    password: str = Field(..., min_length=8)


class RegisterResponse(BaseModel):
    """Schema for registration response."""

    id: str
    email: str


class LoginRequest(BaseModel):
    """Schema for login request."""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Schema for login response."""

    token: str
    expires_in: int


class LogoutResponse(BaseModel):
    """Schema for logout response."""

    message: str = "Logged out"


class UserResponse(BaseModel):
    """Schema for user response."""

    id: str
    email: str
