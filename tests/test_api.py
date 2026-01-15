"""
Tests para API
"""
import pytest
from fastapi.testclient import TestClient
import sys
sys.path.append('.')

from api.main import app

client = TestClient(app)


def test_root():
    """Test endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    assert "WongPrime" in response.text


def test_health():
    """Test health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_get_stats():
    """Test estadísticas"""
    response = client.get("/estadisticas/")
    assert response.status_code == 200
    data = response.json()
    assert "total_productos" in data
    assert "total_tiendas" in data


def test_get_productos():
    """Test listado de productos"""
    response = client.get("/productos/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
