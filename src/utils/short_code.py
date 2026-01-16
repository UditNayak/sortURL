"""Short code generation utilities."""
import string
import random
from typing import Optional
from src.config import settings


def generate_short_code(length: Optional[int] = None) -> str:
    """Generate a random alphanumeric short code.
    
    Args:
        length: Length of the short code (default from settings)
        
    Returns:
        Random short code
    """
    if length is None:
        length = settings.SHORT_CODE_LENGTH
    
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def is_valid_custom_alias(alias: str) -> bool:
    """Check if a custom alias is valid.
    
    Args:
        alias: Custom alias to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not alias:
        return False
    
    if len(alias) < settings.SHORT_CODE_MIN_LENGTH or len(alias) > settings.SHORT_CODE_MAX_LENGTH:
        return False
    
    # Only alphanumeric and hyphens allowed
    return all(c.isalnum() or c == '-' for c in alias)