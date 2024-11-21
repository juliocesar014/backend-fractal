from django.http import Http404
from ninja import NinjaAPI
from django.shortcuts import get_object_or_404
from .models import Answer, Participant, Question, Choice
from .schemas import AnswerSchema, CreateAnswerSchema, UpdateAnswerSchema
import logging

router = NinjaAPI(urls_namespace="answer")
logger = logging.getLogger(__name__)


@router.post("/", response={201: AnswerSchema, 400: dict, 500: dict})
def create_answer(request, data: CreateAnswerSchema):
    """Create a new answer."""
    try:
        participant = get_object_or_404(Participant, id=data.participant_id)
        question = get_object_or_404(Question, id=data.question_id)
        choice = get_object_or_404(
            Choice, id=data.choice_id, question=question)

        if Answer.objects.filter(participant=participant, question=question).exists():
            return 400, {"error": "This question has already been answered by the participant."}

        answer = Answer.objects.create(
            participant=participant,
            question=question,
            choice=choice,
        )

        return 201, AnswerSchema.from_orm(answer)
    except Http404:
        return 400, {"error": "Invalid participant, question, or choice ID."}
    except Exception as e:
        logger.error(f"Error while creating answer: {e}")
        return 500, {"error": "An error occurred while creating the answer."}


@router.put("/{answer_id}/", response={200: AnswerSchema, 400: dict, 404: dict, 500: dict})
def update_answer(request, answer_id: int, data: UpdateAnswerSchema):
    """Update an existing answer."""
    try:
        answer = get_object_or_404(Answer, id=answer_id)
        choice = get_object_or_404(
            Choice, id=data.choice_id, question=answer.question)

        answer.choice = choice
        answer.save()

        return AnswerSchema.from_orm(answer)
    except Http404:
        return 404, {"error": "Answer or choice not found."}
    except Exception as e:
        logger.error(f"Error while updating answer {answer_id}: {e}")
        return 500, {"error": "An error occurred while updating the answer."}
