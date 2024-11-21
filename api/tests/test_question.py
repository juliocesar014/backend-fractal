import pytest
from api.models import Question, Exam


@pytest.fixture
def create_exam(db):
    return Exam.objects.create(
        name="Test Exam",
        description="Test Description",
        start_date="2024-01-01T10:00:00Z",
        end_date="2024-01-02T10:00:00Z",
    )


@pytest.fixture
def create_questions(db, create_exam):
    return Question.objects.bulk_create([
        Question(exam=create_exam, text="Question 1"),
        Question(exam=create_exam, text="Question 2"),
    ])


@pytest.mark.django_db
def test_list_questions(client, create_questions):
    url = "/api/questions/"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.django_db
def test_create_question(client, create_exam):
    url = "/api/questions/"
    payload = {
        "exam_id": create_exam.id,
        "text": "New Question",
    }
    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "New Question"
    assert data["exam_id"] == create_exam.id


@pytest.mark.django_db
def test_update_question(client, create_questions):
    question = create_questions[0]
    url = f"/api/questions/{question.id}/"
    payload = {
        "text": "Updated Question",
    }
    response = client.put(url, payload, content_type="application/json")
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Updated Question"


@pytest.mark.django_db
def test_delete_question(client, create_questions):
    question = create_questions[0]
    url = f"/api/questions/{question.id}/"
    response = client.delete(url)
    assert response.status_code == 200
    assert response.json() == "Question deleted successfully."
    assert not Question.objects.filter(id=question.id).exists()
