"""Page rendering routes using Jinja2 templates."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from src.services.auth_service import get_current_user
from src.services.url_service import get_user_urls, get_url_stats

router = APIRouter(prefix="/api", tags=["pages"])

# Setup templates
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/home", response_class=HTMLResponse)
async def home_page(request: Request):
    """Render homepage with URL shortening form.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Rendered HTML page
    """
    user = get_current_user(request)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user
    })


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Render analytics dashboard.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Rendered HTML page
    """
    user = get_current_user(request)
    
    # Get URLs
    user_id = user['id'] if user else None
    urls = get_user_urls(user_id)
    
    # Get stats
    stats = get_url_stats()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "urls": urls,
        "total_clicks": stats["total_clicks"],
        "total_urls": stats["total_urls"]
    })


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render login page.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Rendered HTML page or redirect if already logged in
    """
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/api/dashboard", status_code=302)
    
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Render signup page.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Rendered HTML page or redirect if already logged in
    """
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/api/dashboard", status_code=302)
    
    return templates.TemplateResponse("signup.html", {"request": request})