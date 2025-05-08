import pytest
from fastapi.testclient import TestClient

from fast_zero.app import app


@pytest.fixture
def client():
    """Fixture para criar um cliente de teste do FastAPI."""
    return TestClient(app)
