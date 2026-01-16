"""Pydantic models for request/response validation."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# URL Models
class URLCreate(BaseModel):
    """Schema for creating a shortened URL."""
    original_url: str = Field(..., min_length=1, max_length=2048)
    custom_alias: Optional[str] = Field(None, min_length=2, max_length=20)


class URLResponse(BaseModel):
    """Schema for URL response."""
    id: str
    original_url: str
    short_code: str
    custom_alias: bool
    click_count: int
    created_at: str


class URLRedirectResponse(BaseModel):
    """Schema for redirect response."""
    url: str
    short_code: str


# User Models
class UserSignup(BaseModel):
    """Schema for user signup."""
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response."""
    id: str
    email: str
    created_at: str


# Token Models
class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str = "bearer"


# Health Check Models
class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str
    timestamp: str