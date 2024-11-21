import pytest
from api.models import Answer, Participant, Question, Choice


@pytest.fixture
def create_user(db):
    """Fixture to create a user."""
    from api.models import User
    return User.objects.create_user(
        username="participant_user",
        email="participant@example.com",
        password="password123",
        role="participant",
    )


@pytest.fixture
def create_participant(db, create_user):
    """Fixture to create a participant."""
    return Participant.objects.create(user=create_user)


@pytest.fixture
def create_exam(db):
    """Fixture to create an exam."""
    from api.models import Exam
    return Exam.objects.create(
        name="Test Exam",
        description="A test exam description",
        start_date="2024-01-01T10:00:00Z",
        end_date="2024-01-01T12:00:00Z",
    )


@pytest.fixture
def create_participant_with_exam_and_question(db, create_participant, create_exam):
    """Fixture to create a participant with an exam and a question."""
    question = Question.objects.create(
        exam=create_exam,
        text="What is the capital of France?",
    )
    choice1 = Choice.objects.create(
        question=question, text="Paris", is_correct=True)
    choice2 = Choice.objects.create(
        question=question, text="London", is_correct=False)
    return {
        "participant": create_participant,
        "exam": create_exam,
        "question": question,
        "choices": [choice1, choice2],
    }


@pytest.fixture
def create_answer(db, create_participant_with_exam_and_question):
    """Fixture to create an answer."""
    data = create_participant_with_exam_and_question
    return Answer.objects.create(
        participant=data["participant"],
        question=data["question"],
        choice=data["choices"][0],
    )


@pytest.mark.django_db
def test_create_answer(client, create_participant_with_exam_and_question):
    """Test creating an answer."""
    data = create_participant_with_exam_and_question
    url = "/api/answers/"
    payload = {
        "participant_id": data["participant"].id,
        "question_id": data["question"].id,
        "choice_id": data["choices"][0].id,
    }
    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["participant_id"] == data["participant"].id
    assert response_data["question_id"] == data["question"].id
    assert response_data["choice_id"] == data["choices"][0].id


@pytest.mark.django_db
def test_create_answer_duplicate(client, create_answer):
    """Test creating a duplicate answer."""
    url = "/api/answers/"
    payload = {
        "participant_id": create_answer.participant.id,
        "question_id": create_answer.question.id,
        "choice_id": create_answer.choice.id,
    }
    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 400
    assert "already been answered" in response.json()["error"]


@pytest.mark.django_db
def test_create_answer_invalid_choice(client, create_participant_with_exam_and_question):
    """Test creating an answer with an invalid choice (not related to the question)."""
    data = create_participant_with_exam_and_question
    unrelated_choice = Choice.objects.create(
        question=Question.objects.create(
            exam=data["exam"], text="What is 2 + 2?"
        ),
        text="4",
        is_correct=True,
    )
    url = "/api/answers/"
    payload = {
        "participant_id": data["participant"].id,
        "question_id": data["question"].id,
        "choice_id": unrelated_choice.id,
    }
    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 400
    assert "Invalid participant, question, or choice ID." in response.json()[
        "error"]


@pytest.mark.django_db
def test_update_answer(client, create_answer, create_participant_with_exam_and_question):
    """Test updating an existing answer."""
    new_choice = create_participant_with_exam_and_question["choices"][1]
    url = f"/api/answers/{create_answer.id}/"
    payload = {"choice_id": new_choice.id}
    response = client.put(url, payload, content_type="application/json")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["choice_id"] == new_choice.id


@pytest.mark.django_db
def test_update_answer_invalid_choice(client, create_answer):
    """Test updating an answer with an invalid choice (not related to the question)."""
    unrelated_choice = Choice.objects.create(
        question=Question.objects.create(
            exam=create_answer.question.exam,
            text="What is the square root of 16?",
        ),
        text="4",
        is_correct=True,
    )
    url = f"/api/answers/{create_answer.id}/"
    payload = {"choice_id": unrelated_choice.id}
    response = client.put(url, payload, content_type="application/json")
    assert response.status_code == 404
    assert "Answer or choice not found." in response.json()["error"]


@pytest.mark.django_db
def test_update_answer_not_found(client):
    """Test updating a non-existent answer."""
    url = "/api/answers/999/"
    payload = {"choice_id": 1}
    response = client.put(url, payload, content_type="application/json")
    assert response.status_code == 404
    assert "Answer or choice not found." in response.json()["error"]
