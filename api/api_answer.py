from django.http import Http404
from ninja import NinjaAPI
from django.shortcuts import get_object_or_404

from api.api_auth import AuthBearer
from .models import Answer, Participant, Question, Choice
from .schemas import AnswerSchema, CreateAnswerSchema, UpdateAnswerSchema
import logging

router = NinjaAPI(urls_namespace="answer")
logger = logging.getLogger(__name__)


@router.post("/", response={201: AnswerSchema, 400: dict}, auth=AuthBearer())
def create_answer(request, data: CreateAnswerSchema):
    """
    Create an answer for the authenticated participant.
    """
    participant = get_object_or_404(Participant, user=request.user)
    question = get_object_or_404(Question, id=data.question_id)
    choice = get_object_or_404(Choice, id=data.choice_id, question=question)

    if question.exam not in participant.exams.all():
        return 400, {"error": "You are not allowed to answer this question."}

    answer, created = Answer.objects.update_or_create(
        participant=participant,
        question=question,
        defaults={"choice": choice},
    )
    return 201, answer


@router.put("/{answer_id}/", response={200: AnswerSchema, 404: dict}, auth=AuthBearer())
def update_answer(request, answer_id: int, data: UpdateAnswerSchema):
    """
    Update an existing answer for the authenticated participant.
    """
    participant = get_object_or_404(Participant, user=request.user)
    answer = get_object_or_404(Answer, id=answer_id, participant=participant)

    if data.choice_id:
        choice = get_object_or_404(
            Choice, id=data.choice_id, question=answer.question)
        answer.choice = choice

    answer.save()
    return answer
