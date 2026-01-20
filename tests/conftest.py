import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.main import app
from src.database import init_database

# Test environment
os.environ["ENV"] = "test"


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    init_database()


@pytest.fixture
def client():
    return TestClient(app)
