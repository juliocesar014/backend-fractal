import pytest
from api.models import Participant, User, Exam


@pytest.fixture
def create_user(db):
    """Fixture to create a user."""
    return User.objects.create_user(
        username="participant_user",
        email="participant@example.com",
        password="password123",
        role="PARTICIPANT",
    )


@pytest.fixture
def create_exam(db):
    """Fixture to create an exam."""
    return Exam.objects.create(
        name="Sample Exam",
        description="Test Description",
        start_date="2024-01-01T10:00:00Z",
        end_date="2024-01-02T10:00:00Z",
    )


@pytest.fixture
def create_participant(db, create_user, create_exam):
    """Fixture to create a participant."""
    participant = Participant.objects.create(user=create_user)
    participant.exams.add(create_exam)
    return participant


@pytest.fixture
def create_multiple_participants(db, create_exam):
    """Fixture to create multiple participants."""
    users = User.objects.bulk_create([
        User(username="user1", email="user1@example.com", role="PARTICIPANT"),
        User(username="user2", email="user2@example.com", role="PARTICIPANT"),
    ])
    participants = [
        Participant.objects.create(user=users[0]),
        Participant.objects.create(user=users[1]),
    ]
    participants[0].exams.add(create_exam)
    return participants


@pytest.mark.django_db
def test_list_participants(client, create_multiple_participants):
    """Test listing all participants."""
    url = "/api/participants/"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["user_id"] > 0
    assert data[1]["user_id"] > 0


@pytest.mark.django_db
def test_list_participants_search(client, create_multiple_participants):
    """Test listing participants with search."""
    url = "/api/participants/?search=user1"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_id"] > 0


@pytest.mark.django_db
def test_get_participant(client, create_participant):
    """Test retrieving a single participant by ID."""
    url = f"/api/participants/{create_participant.id}/"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == create_participant.user.id
    assert len(data["exams"]) == 1


@pytest.mark.django_db
def test_create_participant(client, create_user, create_exam):
    """Test creating a new participant."""
    url = "/api/participants/"
    payload = {
        "user_id": create_user.id,
        "exam_ids": [create_exam.id],
    }
    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == create_user.id
    assert len(data["exams"]) == 1
    assert data["exams"][0]["id"] == create_exam.id


@pytest.mark.django_db
def test_create_participant_duplicate_user(client, create_participant):
    """Test creating a participant with a user already registered."""
    url = "/api/participants/"
    payload = {
        "user_id": create_participant.user.id,
        "exam_ids": [],
    }
    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 400
    assert response.json()[
        "error"] == "This user is already registered as a participant."


@pytest.mark.django_db
def test_update_participant(client, create_participant, create_exam):
    """Test updating a participant's associated exams."""
    new_exam = Exam.objects.create(
        name="New Exam",
        description="Another test description",
        start_date="2024-02-01T10:00:00Z",
        end_date="2024-02-02T10:00:00Z",
    )
    url = f"/api/participants/{create_participant.id}/"
    payload = {
        "exam_ids": [new_exam.id],
    }
    response = client.put(url, payload, content_type="application/json")
    assert response.status_code == 200
    data = response.json()
    assert len(data["exams"]) == 1
    assert data["exams"][0]["id"] == new_exam.id


@pytest.mark.django_db
def test_delete_participant(client, create_participant):
    """Test deleting a participant."""
    url = f"/api/participants/{create_participant.id}/"
    response = client.delete(url)
    assert response.status_code == 200
    assert response.json() == "Participant deleted successfully."
    assert not Participant.objects.filter(id=create_participant.id).exists()
