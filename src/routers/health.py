"""Health check routes."""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status
from src.models.schemas import HealthResponse
from src.database import get_db_connection

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring.
    
    Returns:
        Health status
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@router.get("/ready", response_model=HealthResponse)
async def readiness_check():
    """Readiness check endpoint for Kubernetes.
    
    Returns:
        Readiness status
        
    Raises:
        HTTPException: If service is not ready
    """
    try:
        # Check if database is accessible
        with get_db_connection() as conn:
            conn.execute("SELECT 1")
        
        return HealthResponse(
            status="ready",
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not ready: {str(e)}"
        )