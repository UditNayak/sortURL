import os

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.database import init_database


# Set test environment
os.environ["ENV"] = "test"


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Initialize SQLite tables once for tests.
    """
    init_database()


@pytest.fixture
def client():
    return TestClient(app)
