"""URL management routes."""
from typing import List
from fastapi import APIRouter, Request, status
from src.models.schemas import URLCreate, URLResponse, URLRedirectResponse
from src.services.url_service import (
    create_shortened_url,
    get_original_url,
    get_user_urls,
    delete_url
)
from src.services.auth_service import get_current_user

router = APIRouter(prefix="/api", tags=["urls"])


@router.post("/shorten", response_model=URLResponse, status_code=status.HTTP_201_CREATED)
async def shorten_url(url_data: URLCreate, request: Request):
    """Create a shortened URL.
    
    Args:
        url_data: URL data to shorten
        request: FastAPI request object
        
    Returns:
        Shortened URL information
    """
    user = get_current_user(request)
    user_id = user['id'] if user else None
    
    return create_shortened_url(url_data, user_id)


@router.get("/redirect/{short_code}", response_model=URLRedirectResponse)
async def get_redirect_url(short_code: str, request: Request):
    """Get the original URL for a short code (for frontend redirect handling).
    
    Args:
        short_code: Short code to look up
        request: FastAPI request object
        
    Returns:
        Original URL and short code
    """
    original_url = get_original_url(short_code, request, track_click=True)
    return URLRedirectResponse(url=original_url, short_code=short_code)


@router.get("/urls", response_model=List[URLResponse])
async def get_urls(request: Request):
    """Get all URLs for the authenticated user or public URLs.
    
    Args:
        request: FastAPI request object
        
    Returns:
        List of URLs
    """
    user = get_current_user(request)
    user_id = user['id'] if user else None
    
    urls = get_user_urls(user_id)
    return [URLResponse(**url) for url in urls]


@router.delete("/urls/{url_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shortened_url(url_id: str, request: Request):
    """Delete a shortened URL.
    
    Args:
        url_id: URL ID to delete
        request: FastAPI request object
    """
    user = get_current_user(request)
    user_id = user['id'] if user else None
    
    delete_url(url_id, user_id)
    return None