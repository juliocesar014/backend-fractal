import pytest
from api.models import Answer, Exam, Participant, Question, Choice, User
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def create_user(db):
    """Create a user with 'participant' role."""
    return User.objects.create_user(
        username="participant_user",
        email="participant@example.com",
        password="password123",
        role="participant",
    )


@pytest.fixture
def get_token(create_user):
    """Generate JWT token for a user."""
    refresh = RefreshToken.for_user(create_user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


@pytest.fixture
def create_participant(db, create_user):
    """Fixture to create a participant."""
    return Participant.objects.create(user=create_user)


@pytest.fixture
def create_exam_and_question(db):
    """Create an exam, question, and choices."""
    exam = Exam.objects.create(
        name="Test Exam",
        description="Test Description",
        start_date="2024-01-01T10:00:00Z",
        end_date="2024-01-01T12:00:00Z",
    )
    question = Question.objects.create(
        exam=exam, text="What is the capital of France?")
    choice1 = Choice.objects.create(
        question=question, text="Paris", is_correct=True)
    choice2 = Choice.objects.create(
        question=question, text="London", is_correct=False)
    return {"exam": exam, "question": question, "choices": [choice1, choice2]}


@pytest.fixture
def create_participant_with_exam_and_question(db, create_participant, create_exam_and_question):
    """Fixture to create a participant associated with an exam and a question."""
    data = create_exam_and_question
    participant = create_participant
    participant.exams.add(data["exam"])
    return {
        "participant": participant,
        "exam": data["exam"],
        "question": data["question"],
        "choices": data["choices"],
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
def test_create_answer_with_authentication(
    client, create_participant_with_exam_and_question, get_token
):
    """Test creating an answer with valid authentication."""
    data = create_participant_with_exam_and_question
    url = "/api/answers/"
    payload = {
        "participant_id": data["participant"].id,
        "question_id": data["question"].id,
        "choice_id": data["choices"][0].id,
    }
    headers = {"HTTP_AUTHORIZATION": f"Bearer {get_token['access']}"}
    response = client.post(
        url, payload, content_type="application/json", **headers)

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["participant_id"] == data["participant"].id
    assert response_data["question_id"] == data["question"].id
    assert response_data["choice_id"] == data["choices"][0].id


@pytest.mark.django_db
def test_create_answer_unauthorized(client, create_participant_with_exam_and_question):
    """Test creating an answer without authorization."""
    data = create_participant_with_exam_and_question
    url = "/api/answers/"
    payload = {
        "participant_id": data["participant"].id,
        "question_id": data["question"].id,
        "choice_id": data["choices"][0].id,
    }
    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 401
    assert response.json().get("detail") == "Unauthorized"


@pytest.mark.django_db
def test_update_answer_with_authentication(
    client, create_answer, create_participant_with_exam_and_question, get_token
):
    """Test updating an existing answer."""
    data = create_participant_with_exam_and_question
    new_choice = data["choices"][1]
    url = f"/api/answers/{create_answer.id}/"
    payload = {"choice_id": new_choice.id}
    headers = {"HTTP_AUTHORIZATION": f"Bearer {get_token['access']}"}
    response = client.put(
        url, payload, content_type="application/json", **headers)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["choice_id"] == new_choice.id


@pytest.mark.django_db
def test_update_answer_unauthorized(client, create_answer):
    """Test updating an answer without authorization."""
    url = f"/api/answers/{create_answer.id}/"
    payload = {"choice_id": 1}
    response = client.put(url, payload, content_type="application/json")
    assert response.status_code == 401
    assert response.json().get("detail") == "Unauthorized"
