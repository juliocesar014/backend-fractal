import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import User


@pytest.mark.django_db
def test_login(client, db):
    """Test user login with valid credentials."""
    User.objects.create_user(username="testuser", password="password123")
    url = "/api/auth/login"
    payload = {"username": "testuser", "password": "password123"}
    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 200
    data = response.json()
    assert "access" in data
    assert "refresh" in data


@pytest.mark.django_db
def test_login_invalid_credentials(client):
    """Test user login with invalid credentials."""
    url = "/api/auth/login"
    payload = {"username": "invaliduser", "password": "wrongpassword"}
    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 401
    assert "error" in response.json()


@pytest.mark.django_db
def test_refresh_token(client, db):
    """Test refreshing an access token."""
    user = User.objects.create_user(
        username="testuser", password="password123")
    refresh_token = RefreshToken.for_user(user)
    url = "/api/auth/refresh"
    payload = {"refresh": str(refresh_token)}
    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 200
    data = response.json()
    assert "access" in data
    assert "refresh" in data
