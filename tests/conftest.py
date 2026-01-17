import os
import pytest
from fastapi.testclient import TestClient

# Force test env
os.environ["ENV"] = "test"

from src.main import app
from src.database import init_database


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Initialize SQLite tables once for tests.
    """
    init_database()


@pytest.fixture
def client():
    return TestClient(app)
