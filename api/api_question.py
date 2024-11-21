

from django.http import Http404
from ninja import NinjaAPI, Query
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from .models import Question, Exam
from .schemas import QuestionSchema, CreateQuestionSchema, UpdateQuestionSchema
from django.core.paginator import Paginator, EmptyPage
from typing import Optional
import logging

router = NinjaAPI(urls_namespace="questions")


logger = logging.getLogger(__name__)


@router.get("/", response={200: list[QuestionSchema], 400: dict, 500: dict})
def list_questions(
    request,
    search: Optional[str] = Query(None),
    order: Optional[str] = Query(None),
    page: int = Query(1),
    page_size: int = Query(10),
):
    """List all questions with optional search, sorting, and pagination."""
    try:
        questions = Question.objects.all()

        if search:
            questions = questions.filter(text__icontains=search)

        valid_order_fields = ["text", "exam_id", "-text", "-exam_id"]
        if order:
            if order in valid_order_fields:
                questions = questions.order_by(order)
            else:
                return 400, {"error": f"Invalid order field. Allowed: {', '.join(valid_order_fields)}"}

        paginator = Paginator(questions, page_size)
        try:
            paginated_questions = paginator.page(page)
        except EmptyPage:
            return 400, {"error": "Page number out of range."}

        return [QuestionSchema.from_orm(q) for q in paginated_questions]
    except Exception as e:
        logger.error(f"Error while listing questions: {e}")
        return 500, {"error": "An error occurred while listing questions."}


@router.get("/{question_id}/", response={200: QuestionSchema, 404: dict, 500: dict})
def get_question(request, question_id: int):
    """Retrieve a question by ID."""
    try:
        question = get_object_or_404(Question, id=question_id)
        return question
    except Http404:
        return 404, {"error": "Question not found."}
    except Exception as e:
        logger.error(f"Error while retrieving question {question_id}: {e}")
        return 500, {"error": "An error occurred while retrieving the question."}


@router.post("/", response={201: QuestionSchema, 400: dict, 500: dict})
def create_question(request, data: CreateQuestionSchema):
    """Create a new question."""
    try:
        exam = get_object_or_404(Exam, id=data.exam_id)
        question = Question.objects.create(exam=exam, text=data.text)
        return 201, question
    except IntegrityError as e:
        logger.error(f"Integrity error while creating question: {e}")
        return 400, {"error": "A question with similar attributes already exists."}
    except Exception as e:
        logger.error(f"Error while creating question: {e}")
        return 500, {"error": "An error occurred while creating the question."}


@router.put("/{question_id}/", response={200: QuestionSchema, 400: dict, 404: dict, 500: dict})
def update_question(request, question_id: int, data: UpdateQuestionSchema):
    """Update an existing question."""
    try:
        question = get_object_or_404(Question, id=question_id)

        for attr, value in data.model_dump(exclude_unset=True).items():
            setattr(question, attr, value)

        question.save()
        return question
    except Http404:
        return 404, {"error": "Question not found."}
    except IntegrityError as e:
        logger.error(f"Integrity error while updating question {
                     question_id}: {e}")
        return 400, {"error": "Integrity error occurred while updating the question."}
    except Exception as e:
        logger.error(f"Error while updating question {question_id}: {e}")
        return 500, {"error": "An error occurred while updating the question."}


@router.delete("/{question_id}/", response={200: str, 404: dict, 500: dict})
def delete_question(request, question_id: int):
    """Delete a question."""
    try:
        question = get_object_or_404(Question, id=question_id)
        question.delete()
        return 200, "Question deleted successfully."
    except Http404:
        return 404, {"error": "Question not found."}
    except Exception as e:
        logger.error(f"Error while deleting question {question_id}: {e}")
        return 500, {"error": "An error occurred while deleting the question."}
