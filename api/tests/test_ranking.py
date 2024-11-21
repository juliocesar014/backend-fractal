import pytest
from api.models import Result, Exam, Participant, User


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
def create_results(db, create_exam, create_participant):
    """Fixture to create results for ranking."""
    from api.models import Participant, User

    participant1 = create_participant
    participant2 = Participant.objects.create(
        user=User.objects.create_user(
            username="user2", email="user2@example.com", password="password"
        )
    )
    participant3 = Participant.objects.create(
        user=User.objects.create_user(
            username="user3", email="user3@example.com", password="password"
        )
    )

    Result.objects.create(participant=participant1,
                          exam=create_exam, score=80, max_score=100)
    Result.objects.create(participant=participant2,
                          exam=create_exam, score=90, max_score=100)
    Result.objects.create(participant=participant3,
                          exam=create_exam, score=70, max_score=100)


@pytest.mark.django_db
def test_get_ranking(client, create_results, create_exam):
    """Test retrieving the ranking for an exam."""
    url = f"/api/rankings/{create_exam.id}/"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 3
    assert data[0]["username"] == "user2"
    assert data[0]["score"] == 90
    assert data[0]["rank"] == 1

    assert data[1]["username"] == "participant_user"
    assert data[1]["score"] == 80
    assert data[1]["rank"] == 2

    assert data[2]["username"] == "user3"
    assert data[2]["score"] == 70
    assert data[2]["rank"] == 3


@pytest.mark.django_db
def test_get_ranking_no_results(client, create_exam):
    """Test retrieving the ranking for an exam with no results."""
    url = f"/api/rankings/{create_exam.id}/"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


@pytest.mark.django_db
def test_get_ranking_invalid_exam(client):
    """Test retrieving the ranking for an invalid exam."""
    url = "/api/rankings/999/"
    response = client.get(url)
    assert response.status_code == 404
    assert "Exam not found." in response.json()["error"]
