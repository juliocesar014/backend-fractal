import pytest
from api.models import User


@pytest.fixture
def create_user(db):
    """Fixture to create a user."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password123",
        role="ADMIN",
    )


@pytest.mark.django_db
def test_list_users(client, create_user):
    """Test listing all users."""
    url = "/api/users"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["username"] == "testuser"


@pytest.mark.django_db
def test_get_user(client, create_user):
    """Test retrieving a single user by ID."""
    url = f"/api/users/{create_user.id}/"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


@pytest.mark.django_db
def test_create_user(client):
    """Test creating a new user."""
    url = "/api/users"
    payload = {
        "username": "user",
        "email": "user@test.com",
        "first_name": "User",
        "last_name": "Teste",
        "password": "@user123",
        "role": "ADMIN"
    }
    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "user"
    assert data["email"] == "user@test.com"


@pytest.mark.django_db
def test_update_user(client, create_user):
    """Test updating an existing user."""
    url = f"/api/users/{create_user.id}/"
    payload = {
        "first_name": "UpdatedFirstName",
        "last_name": "UpdatedLastName",
        "email": "updated@example.com",
        "role": "ADMIN",
    }
    response = client.put(url, payload, content_type="application/json")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "updated@example.com"
    assert data["first_name"] == "UpdatedFirstName"
    assert data["last_name"] == "UpdatedLastName"
    assert data["role"] == "ADMIN"


@pytest.mark.django_db
def test_delete_user(client, create_user):
    """Test deleting a user."""
    url = f"/api/users/{create_user.id}/"
    response = client.delete(url)
    assert response.status_code == 200
    assert response.json() == "User successfully deleted."
    assert not User.objects.filter(id=create_user.id).exists()
