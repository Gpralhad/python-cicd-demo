import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test that the home page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome" in response.data

def test_health_check(client):
    """Test the application health endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    assert b"OK" in response.data
