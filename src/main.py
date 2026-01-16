"""Main FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware

from src.config import settings
from src.database import init_database
from src.routers import auth, urls, health, pages
from src.services.url_service import get_original_url

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    init_database()
    logger.info("Database initialized")
    logger.info(f"{settings.APP_NAME} started")
    yield
    # Shutdown
    logger.info(f"{settings.APP_NAME} shutting down")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Production-grade URL Shortener built with FastAPI + Jinja2 + SQLite",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(urls.router)
app.include_router(health.router)
app.include_router(pages.router)


# Root redirect routes (non-API)
@app.get("/")
async def root():
    """Redirect root to homepage."""
    return RedirectResponse(url="/api/home")


@app.get("/home")
async def home():
    """Redirect /home to /api/home."""
    return RedirectResponse(url="/api/home")


@app.get("/{short_code}")
async def redirect_short_url(short_code: str, request: Request):
    """Redirect short code to original URL.
    
    Args:
        short_code: Short code to redirect
        request: FastAPI request object
        
    Returns:
        Redirect to original URL
    """
    original_url = get_original_url(short_code, request, track_click=True)
    return RedirectResponse(url=original_url, status_code=302)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )