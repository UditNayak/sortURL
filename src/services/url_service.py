"""URL shortening service for business logic."""
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status, Request

from src.database import get_db_connection
from src.utils.short_code import generate_short_code, is_valid_custom_alias
from src.models.schemas import URLCreate, URLResponse


def create_shortened_url(url_data: URLCreate, user_id: Optional[str] = None) -> URLResponse:
    """Create a shortened URL.
    
    Args:
        url_data: URL creation data
        user_id: Optional user ID for authenticated users
        
    Returns:
        Created URL information
        
    Raises:
        HTTPException: If custom alias is invalid or already taken
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Handle custom alias
        if url_data.custom_alias:
            if not is_valid_custom_alias(url_data.custom_alias):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Custom alias can only contain letters, numbers, and hyphens"
                )
            
            # Check if custom alias already exists
            cursor.execute("SELECT id FROM urls WHERE short_code = ?", (url_data.custom_alias,))
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Custom alias already taken"
                )
            
            short_code = url_data.custom_alias
            custom_alias = True
        else:
            # Generate random short code
            while True:
                short_code = generate_short_code()
                cursor.execute("SELECT id FROM urls WHERE short_code = ?", (short_code,))
                if not cursor.fetchone():
                    break
            custom_alias = False
        
        # Create URL entry
        url_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        
        cursor.execute(
            """INSERT INTO urls (id, original_url, short_code, custom_alias, user_id, created_at, click_count)
               VALUES (?, ?, ?, ?, ?, ?, 0)""",
            (url_id, url_data.original_url, short_code, custom_alias, user_id, created_at)
        )
        
        conn.commit()
        
        return URLResponse(
            id=url_id,
            original_url=url_data.original_url,
            short_code=short_code,
            custom_alias=custom_alias,
            click_count=0,
            created_at=created_at
        )


def get_original_url(short_code: str, request: Request, track_click: bool = True) -> str:
    """Get original URL from short code and optionally track click.
    
    Args:
        short_code: Short code to look up
        request: FastAPI request object for tracking
        track_click: Whether to track this as a click
        
    Returns:
        Original URL
        
    Raises:
        HTTPException: If short code not found
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, original_url FROM urls WHERE short_code = ?", (short_code,))
        url = cursor.fetchone()
        
        if not url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Short URL not found"
            )
        
        if track_click:
            # Update click count
            cursor.execute("UPDATE urls SET click_count = click_count + 1 WHERE id = ?", (url['id'],))
            
            # Track click details
            click_id = str(uuid.uuid4())
            clicked_at = datetime.now(timezone.utc).isoformat()
            referrer = request.headers.get("referer", "")
            user_agent = request.headers.get("user-agent", "")
            
            cursor.execute(
                """INSERT INTO clicks (id, url_id, clicked_at, referrer, user_agent)
                   VALUES (?, ?, ?, ?, ?)""",
                (click_id, url['id'], clicked_at, referrer, user_agent)
            )
            
            conn.commit()
        
        return url['original_url']


def get_user_urls(user_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Get URLs for a user or public URLs.
    
    Args:
        user_id: User ID to filter by (None for public URLs)
        limit: Maximum number of URLs to return
        
    Returns:
        List of URLs with their information
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute(
                """SELECT id, original_url, short_code, custom_alias, click_count, created_at
                   FROM urls WHERE user_id = ?
                   ORDER BY created_at DESC""",
                (user_id,)
            )
        else:
            cursor.execute(
                """SELECT id, original_url, short_code, custom_alias, click_count, created_at
                   FROM urls WHERE user_id IS NULL
                   ORDER BY created_at DESC LIMIT ?""",
                (limit,)
            )
        
        return [dict(row) for row in cursor.fetchall()]


def delete_url(url_id: str, user_id: Optional[str] = None) -> None:
    """Delete a URL.
    
    Args:
        url_id: URL ID to delete
        user_id: User ID for authorization check
        
    Raises:
        HTTPException: If URL not found or user not authorized
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if URL exists and user owns it
        cursor.execute("SELECT user_id FROM urls WHERE id = ?", (url_id,))
        url = cursor.fetchone()
        
        if not url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="URL not found"
            )
        
        # Only allow deletion if user owns it or it's public
        if url['user_id'] and (not user_id or url['user_id'] != user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this URL"
            )
        
        cursor.execute("DELETE FROM urls WHERE id = ?", (url_id,))
        cursor.execute("DELETE FROM clicks WHERE url_id = ?", (url_id,))
        
        conn.commit()


def get_url_stats() -> Dict[str, int]:
    """Get overall URL statistics.
    
    Returns:
        Dictionary with total clicks and total URLs
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT SUM(click_count) as total_clicks FROM urls")
        total_clicks = cursor.fetchone()['total_clicks'] or 0
        
        cursor.execute("SELECT COUNT(*) as total_urls FROM urls")
        total_urls = cursor.fetchone()['total_urls']
        
        return {
            "total_clicks": total_clicks,
            "total_urls": total_urls
        }