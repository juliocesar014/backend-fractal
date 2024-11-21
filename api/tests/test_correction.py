import pytest
from api.models import Participant, Result, Answer, Choice, Question, Exam, User


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
def create_exam_with_questions_and_choices(db, create_exam):
    """Fixture to create an exam with questions and choices."""
    question1 = Question.objects.create(
        exam=create_exam, text="What is 2 + 2?")
    choice1_q1 = Choice.objects.create(
        question=question1, text="4", is_correct=True)
    choice2_q1 = Choice.objects.create(
        question=question1, text="5", is_correct=False)

    question2 = Question.objects.create(
        exam=create_exam, text="What is the capital of France?")
    choice1_q2 = Choice.objects.create(
        question=question2, text="Paris", is_correct=True)
    choice2_q2 = Choice.objects.create(
        question=question2, text="London", is_correct=False)

    return {
        "exam": create_exam,
        "questions": [question1, question2],
        "choices": {
            question1.id: [choice1_q1, choice2_q1],
            question2.id: [choice1_q2, choice2_q2],
        },
    }


@pytest.fixture
def create_answers_for_exam(db, create_participant, create_exam_with_questions_and_choices):
    """Fixture to create answers for an exam."""
    data = create_exam_with_questions_and_choices
    participant = create_participant

    # Answer question 1 correctly
    Answer.objects.create(
        participant=participant,
        question=data["questions"][0],
        # Correct choice for question 1
        choice=data["choices"][data["questions"][0].id][0],
    )

    # Answer question 2 incorrectly
    Answer.objects.create(
        participant=participant,
        question=data["questions"][1],
        # Incorrect choice for question 2
        choice=data["choices"][data["questions"][1].id][1],
    )

    return {
        "participant": participant,
        "exam": data["exam"],
        "questions": data["questions"],
        "choices": data["choices"],
    }


@pytest.mark.django_db
def test_trigger_correction(client, create_answers_for_exam):
    """Test the correction process for an exam."""
    data = create_answers_for_exam
    url = f"/api/corrections/{data['participant'].id}/exam/{data['exam'].id}/"

    response = client.post(url)
    assert response.status_code == 200

    result = Result.objects.get(
        participant=data["participant"], exam=data["exam"])
    assert result.score == 1
    assert result.max_score == 2
    assert response.json()["score"] == 1
    assert response.json()["max_score"] == 2


@pytest.mark.django_db
def test_trigger_correction_no_answers(client, create_participant, create_exam):
    """Test the correction process when no answers exist for the participant."""
    url = f"/api/corrections/{create_participant.id}/exam/{create_exam.id}/"

    response = client.post(url)
    assert response.status_code == 200

    result = Result.objects.get(
        participant=create_participant, exam=create_exam)
    assert result.score == 0
    assert result.max_score == 0


@pytest.mark.django_db
def test_trigger_correction_invalid_participant(client, create_exam):
    """Test correction process with an invalid participant."""
    url = f"/api/corrections/999/exam/{
        create_exam.id}/"  # Invalid participant ID

    response = client.post(url)
    assert response.status_code == 404
    assert "Participant not found." in response.json()["error"]


@pytest.mark.django_db
def test_trigger_correction_invalid_exam(client, create_participant):
    """Test correction process with an invalid exam."""
    url = f"/api/corrections/{create_participant.id}/exam/999/"

    response = client.post(url)
    assert response.status_code == 404
    assert "Exam not found." in response.json()["error"]


@pytest.mark.django_db
def test_trigger_correction_existing_result(client, create_answers_for_exam):
    """Test correction process updates an existing result."""
    data = create_answers_for_exam

    url = f"/api/corrections/{data['participant'].id}/exam/{data['exam'].id}/"
    response = client.post(url)
    assert response.status_code == 200

    result = Result.objects.get(
        participant=data["participant"], exam=data["exam"])
    assert result.score == 1
    assert result.max_score == 2

    Answer.objects.filter(
        participant=data["participant"], question=data["questions"][1]
    ).update(choice=data["choices"][data["questions"][1].id][0])

    response = client.post(url)
    assert response.status_code == 200

    result.refresh_from_db()
    assert result.score == 2
    assert result.max_score == 2
