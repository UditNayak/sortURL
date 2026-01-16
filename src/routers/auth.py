"""Authentication routes."""
from typing import Literal
from fastapi import APIRouter, Response, status
from src.models.schemas import UserSignup, UserLogin, TokenResponse
from src.services.auth_service import create_user, authenticate_user
from src.utils.jwt_handler import create_access_token
from src.config import settings

router = APIRouter(prefix="/api", tags=["authentication"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignup, response: Response):
    """Register a new user.
    
    Args:
        user_data: User signup information
        response: FastAPI response object
        
    Returns:
        Access token
    """
    user = create_user(user_data)
    
    # Create access token
    access_token = create_access_token(data={"sub": user["id"]})

    # Ensure your settings.COOKIE_SAMESITE is one of these values
    samesite: Literal['lax', 'strict', 'none'] = settings.COOKIE_SAMESITE # type: ignore
    
    # Set cookie
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=access_token,
        httponly=settings.COOKIE_HTTPONLY,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite=samesite
    )
    
    return TokenResponse(access_token=access_token)


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, response: Response):
    """Authenticate a user.
    
    Args:
        user_data: User login credentials
        response: FastAPI response object
        
    Returns:
        Access token
    """
    user = authenticate_user(user_data)
    
    # Create access token
    access_token = create_access_token(data={"sub": user["id"]})

    # Ensure your settings.COOKIE_SAMESITE is one of these values
    samesite: Literal['lax', 'strict', 'none'] = settings.COOKIE_SAMESITE # type: ignore
    
    # Set cookie
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=access_token,
        httponly=settings.COOKIE_HTTPONLY,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite=samesite
    )
    
    return TokenResponse(access_token=access_token)


@router.post("/logout")
async def logout(response: Response):
    """Logout user by deleting the access token cookie.
    
    Args:
        response: FastAPI response object
        
    Returns:
        Success message
    """
    response.delete_cookie(key=settings.COOKIE_NAME)
    return {"message": "Logged out successfully"}