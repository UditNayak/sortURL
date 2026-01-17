from fastapi import Request
from src.models.schemas import URLCreate
from src.services.url_service import create_shortened_url, get_original_url


def _dummy_request() -> Request:
    """
    Minimal FastAPI Request object for service testing.
    """
    scope = {
        "type": "http",
        "headers": [],
        "method": "GET",
        "path": "/",
    }
    return Request(scope)


def test_create_and_resolve_short_url_service():
    url_data = URLCreate(original_url="https://example.com", custom_alias=None)

    created = create_shortened_url(url_data)
    assert created.short_code is not None

    original = get_original_url(
        short_code=created.short_code,
        request=_dummy_request(),
        track_click=False,
    )

    assert original == "https://example.com"
