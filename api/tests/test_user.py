import pytest
from api.models import User


@pytest.fixture
def create_users(db):
    """Fixture to create multiple test users."""
    return User.objects.bulk_create([
        User(username="admin", email="admin@example.com", role="ADMIN"),
        User(username="user1", email="user1@example.com", role="PARTICIPANT"),
        User(username="user2", email="user2@example.com", role="PARTICIPANT"),
        User(username="alpha", email="alpha@example.com", role="ADMIN"),
    ])


@pytest.fixture
def create_user(db):
    """Fixture to create a single test user."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password123",
        role="ADMIN",
    )


@pytest.mark.django_db
def test_list_users(client, create_users):
    """Test listing all users."""
    url = "/api/users"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4


@pytest.mark.django_db
def test_list_users_search(client, create_users):
    """Test listing users with search functionality."""
    url = "/api/users?search=user"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    usernames = [user["username"] for user in data]
    assert "user1" in usernames
    assert "user2" in usernames


@pytest.mark.django_db
def test_list_users_order(client, create_users):
    """Test listing users with ordering."""
    url = "/api/users?order=username"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    usernames = [user["username"] for user in data]
    assert usernames == ["admin", "alpha", "user1", "user2"]


@pytest.mark.django_db
def test_list_users_pagination(client, create_users):
    """Test listing users with pagination."""
    url = "/api/users?page=1&page_size=2"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["username"] == "admin"
    assert data[1]["username"] == "user1"

    url = "/api/users?page=2&page_size=2"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["username"] == "user2"
    assert data[1]["username"] == "alpha"


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
        "last_name": "Test",
        "password": "@user123",
        "role": "ADMIN"
    }
    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "user"
    assert data["email"] == "user@test.com"


@pytest.mark.django_db
def test_create_user_duplicate_username(client, create_user):
    """Test creating a user with duplicate username."""
    url = "/api/users"
    payload = {
        "username": "testuser",
        "email": "newemail@test.com",
        "first_name": "User",
        "last_name": "Test",
        "password": "@user123",
        "role": "ADMIN",
    }
    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 400
    assert "already exists" in response.json()["error"]


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


@pytest.mark.django_db
def test_delete_user_not_found(client):
    """Test deleting a user that does not exist."""
    url = "/api/users/999/"
    response = client.delete(url)
    assert response.status_code == 404
    assert response.json()["error"] == "User not found."
