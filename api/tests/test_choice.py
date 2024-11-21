import pytest
from api.models import Choice, Question, Exam


@pytest.fixture
def create_exam(db):
    """Fixture to create an exam."""
    return Exam.objects.create(
        name="Test Exam",
        description="Test Description",
        start_date="2024-01-01T10:00:00Z",
        end_date="2024-01-02T10:00:00Z",
    )


@pytest.fixture
def create_question(db, create_exam):
    """Fixture to create a question."""
    return Question.objects.create(
        exam=create_exam,
        text="Test Question",
    )


@pytest.fixture
def create_choices(db, create_question):
    """Fixture to create multiple choices."""
    return Choice.objects.bulk_create([
        Choice(question=create_question, text="Choice 1", is_correct=False),
        Choice(question=create_question, text="Choice 2", is_correct=True),
        Choice(question=create_question, text="Choice 3", is_correct=False),
    ])


@pytest.mark.django_db
def test_list_choices(client, create_choices):
    """Test listing all choices."""
    url = "/api/choices/"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["text"] == "Choice 1"
    assert data[1]["text"] == "Choice 2"
    assert data[2]["text"] == "Choice 3"


@pytest.mark.django_db
def test_list_choices_search(client, create_choices):
    """Test listing choices with search."""
    url = "/api/choices/?search=Choice 2"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["text"] == "Choice 2"
    assert data[0]["is_correct"] is True


@pytest.mark.django_db
def test_list_choices_pagination(client, create_choices):
    """Test listing choices with pagination."""
    url = "/api/choices/?page=1&page_size=2"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["text"] == "Choice 1"
    assert data[1]["text"] == "Choice 2"

    url = "/api/choices/?page=2&page_size=2"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["text"] == "Choice 3"


@pytest.mark.django_db
def test_get_choice(client, create_choices):
    """Test retrieving a single choice by ID."""
    choice = create_choices[1]
    url = f"/api/choices/{choice.id}/"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Choice 2"
    assert data["is_correct"] is True


@pytest.mark.django_db
def test_create_choice(client, create_question):
    """Test creating a new choice."""
    url = "/api/choices/"
    payload = {
        "question_id": create_question.id,
        "text": "New Choice",
        "is_correct": True,
    }
    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "New Choice"
    assert data["is_correct"] is True


@pytest.mark.django_db
def test_create_choice_duplicate_correct_choice(client, create_question, create_choices):
    """Test creating a duplicate correct choice for the same question."""
    url = "/api/choices/"
    payload = {
        "question_id": create_question.id,
        "text": "Another Correct Choice",
        "is_correct": True,
    }
    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 400
    assert response.json()[
        "error"] == "There is already a correct choice for this question."


@pytest.mark.django_db
def test_update_choice(client, create_choices):
    """Test updating an existing choice."""
    choice = create_choices[0]
    url = f"/api/choices/{choice.id}/"
    payload = {
        "text": "Updated Choice",
        "is_correct": True,
    }
    response = client.put(url, payload, content_type="application/json")
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Updated Choice"
    assert data["is_correct"] is True


@pytest.mark.django_db
def test_update_choice_duplicate_correct_choice(client, create_choices):
    """Test updating a choice to be correct when another correct choice exists."""
    choice = create_choices[1]
    url = f"/api/choices/{choice.id}/"
    payload = {
        "is_correct": True,
    }
    response = client.put(url, payload, content_type="application/json")
    assert response.status_code == 400
    assert response.json()[
        "error"] == "There is already a correct choice for this question."


@pytest.mark.django_db
def test_delete_choice(client, create_choices):
    """Test deleting a choice."""
    choice = create_choices[1]
    url = f"/api/choices/{choice.id}/"
    response = client.delete(url)
    assert response.status_code == 200
    assert response.json() == "Choice deleted successfully."
    assert not Choice.objects.filter(id=choice.id).exists()
