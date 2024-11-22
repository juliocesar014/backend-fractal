import logging
from django.db import IntegrityError
from django.http import Http404
from ninja import NinjaAPI, Query
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import get_object_or_404
from typing import Optional

from api.api_auth import AuthBearer
from .models import Exam, Participant
from .schemas import ExamSchema, CreateExamSchema, UpdateExamSchema
from typing import List


router = NinjaAPI(urls_namespace="exams")
logger = logging.getLogger(__name__)


@router.get("/me/", response=List[ExamSchema], auth=AuthBearer())
def list_participant_exams(request):
    """
    List all exams the authenticated participant is enrolled in.
    """
    logger.debug(f"Authenticated user: {request.user}")
    participant = get_object_or_404(Participant, user=request.user)
    exams = Exam.objects.filter(participants=participant)
    logger.debug(f"Exams retrieved: {exams}")
    return exams


@router.get("/", response={200: list[ExamSchema], 500: dict})
def list_exams(
    request,
    search: Optional[str] = Query(None),
    order: Optional[str] = Query(None),
    page: int = Query(1),
    page_size: int = Query(10),
):
    """List all exams with search, sorting, and pagination."""
    try:
        exams = Exam.objects.all()

        if search:
            exams = exams.filter(name__icontains=search)

        if order:
            valid_order_fields = ["name", "-name", "start_date", "-start_date"]
            if order in valid_order_fields:
                exams = exams.order_by(order)
            else:
                return 400, {"error": f"Invalid order field. Allowed: {', '.join(valid_order_fields)}"}

        paginator = Paginator(exams, page_size)
        try:
            paginated_exams = paginator.page(page)
        except EmptyPage:
            return 400, {"error": "Page number out of range."}

        return [ExamSchema.from_orm(exam) for exam in paginated_exams]
    except Exception as e:
        return 500, {"error": f"An error occurred while listing exams: {e}"}


@router.get("/{exam_id}/", response={200: ExamSchema, 404: dict, 500: dict})
def get_exam(request, exam_id: int):
    """Retrieve a single exam by ID."""
    try:
        exam = get_object_or_404(Exam, id=exam_id)
        return exam
    except Exception as e:
        return 500, {"error": f"An error occurred while retrieving the exam: {e}"}


@router.post("/", response={201: ExamSchema, 400: dict, 500: dict})
def create_exam(request, data: CreateExamSchema):
    """Create a new exam."""
    try:
        exam = Exam.objects.create(**data.model_dump())
        return 201, exam
    except IntegrityError as e:
        return 400, {"error": "An exam with this name already exists."}
    except Exception as e:
        return 500, {"error": f"An error occurred while creating the exam: {e}"}


@router.put("/{exam_id}/", response={200: ExamSchema, 400: dict, 404: dict, 500: dict})
def update_exam(request, exam_id: int, data: UpdateExamSchema):
    """Update an existing exam."""
    try:
        exam = get_object_or_404(Exam, id=exam_id)
        for attr, value in data.model_dump(exclude_unset=True).items():
            setattr(exam, attr, value)
        exam.save()
        return exam
    except Http404:
        return 404, {"error": "Exam not found."}
    except Exception as e:
        return 500, {"error": f"An error occurred while updating the exam: {e}"}


@router.delete("/{exam_id}/", response={200: str, 404: dict, 500: dict})
def delete_exam(request, exam_id: int):
    """Delete an exam."""
    try:
        exam = get_object_or_404(Exam, id=exam_id)
        exam.delete()
        return 200, "Exam successfully deleted."
    except Http404:
        return 404, {"error": "Exam not found."}
    except Exception as e:
        return 500, {"error": f"An error occurred while deleting the exam: {e}"}
