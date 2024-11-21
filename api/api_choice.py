from django.http import Http404
from ninja import NinjaAPI, Query
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from .models import Choice, Question
from .schemas import ChoiceSchema, CreateChoiceSchema, UpdateChoiceSchema
from django.core.paginator import Paginator, EmptyPage
from typing import Optional
import logging

router = NinjaAPI(urls_namespace="choices")
logger = logging.getLogger(__name__)


@router.get("/", response={200: list[ChoiceSchema], 400: dict, 500: dict})
def list_choices(
    request,
    search: Optional[str] = Query(None),
    order: Optional[str] = Query(None),
    page: int = Query(1),
    page_size: int = Query(10),
):
    """List all choices with optional search, sorting, and pagination."""
    try:
        choices = Choice.objects.all()

        if search:
            choices = choices.filter(text__icontains=search)
        # Ordenação
        valid_order_fields = ["text", "question_id", "-text", "-question_id"]
        if order:
            if order in valid_order_fields:
                choices = choices.order_by(order)
            else:
                return 400, {"error": f"Invalid order field. Allowed: {', '.join(valid_order_fields)}"}

        # Paginação
        paginator = Paginator(choices, page_size)
        try:
            paginated_choices = paginator.page(page)
        except EmptyPage:
            return 400, {"error": "Page number out of range."}

        return [ChoiceSchema.from_orm(c) for c in paginated_choices]
    except Exception as e:
        logger.error(f"Error while listing choices: {e}")
        return 500, {"error": "An error occurred while listing choices."}


@router.get("/{choice_id}/", response={200: ChoiceSchema, 404: dict, 500: dict})
def get_choice(request, choice_id: int):
    """Retrieve a choice by ID."""
    try:
        choice = get_object_or_404(Choice, id=choice_id)
        return choice
    except Http404:
        return 404, {"error": "Choice not found."}
    except Exception as e:
        logger.error(f"Error while retrieving choice {choice_id}: {e}")
        return 500, {"error": "An error occurred while retrieving the choice."}


@router.post("/", response={201: ChoiceSchema, 400: dict, 500: dict})
def create_choice(request, data: CreateChoiceSchema):
    """Create a new choice."""
    try:
        question = get_object_or_404(Question, id=data.question_id)

        if data.is_correct and Choice.objects.filter(question=question, is_correct=True).exists():
            return 400, {"error": "There is already a correct choice for this question."}

        choice = Choice.objects.create(
            question=question, text=data.text, is_correct=data.is_correct)
        return 201, choice
    except IntegrityError as e:
        logger.error(f"Integrity error while creating choice: {e}")
        return 400, {"error": "A choice with similar attributes already exists."}
    except Exception as e:
        logger.error(f"Error while creating choice: {e}")
        return 500, {"error": "An error occurred while creating the choice."}


@router.put("/{choice_id}/", response={200: ChoiceSchema, 400: dict, 404: dict, 500: dict})
def update_choice(request, choice_id: int, data: UpdateChoiceSchema):
    """Update an existing choice."""
    try:
        choice = get_object_or_404(Choice, id=choice_id)

        if data.is_correct and choice.is_correct:
            if Choice.objects.filter(question=choice.question, is_correct=True).exists():
                return 400, {"error": "There is already a correct choice for this question."}

        for attr, value in data.model_dump(exclude_unset=True).items():
            setattr(choice, attr, value)

        choice.save()
        return choice
    except Http404:
        return 404, {"error": "Choice not found."}
    except IntegrityError as e:
        logger.error(f"Integrity error while updating choice {choice_id}: {e}")
        return 400, {"error": "Integrity error occurred while updating the choice."}
    except Exception as e:
        logger.error(f"Error while updating choice {choice_id}: {e}")
        return 500, {"error": "An error occurred while updating the choice."}


@router.delete("/{choice_id}/", response={200: str, 404: dict, 500: dict})
def delete_choice(request, choice_id: int):
    """Delete a choice."""
    try:
        choice = get_object_or_404(Choice, id=choice_id)
        choice.delete()
        return 200, "Choice deleted successfully."
    except Http404:
        return 404, {"error": "Choice not found."}
    except Exception as e:
        logger.error(f"Error while deleting choice {choice_id}: {e}")
        return 500, {"error": "An error occurred while deleting the choice."}
