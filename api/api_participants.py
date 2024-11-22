from django.http import Http404
from ninja import NinjaAPI, Query
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from .models import Participant, User, Exam
from .schemas import ExamSchema, ParticipantSchema, CreateParticipantSchema, UpdateParticipantSchema
from django.core.paginator import Paginator, EmptyPage
from typing import Optional
import logging
from ninja.decorators import decorate_view
from django.views.decorators.cache import cache_page

router = NinjaAPI(urls_namespace="participants")
logger = logging.getLogger(__name__)


@router.get("/", response={200: list[ParticipantSchema], 400: dict, 500: dict})
@decorate_view(cache_page(60*15))
def list_participants(
    request,
    search: Optional[str] = Query(None),
    page: int = Query(1),
    page_size: int = Query(10),
):
    """List all participants with optional search and pagination."""
    try:
        participants = Participant.objects.select_related(
            "user"
        ).prefetch_related("exams").all()

        if search:
            participants = participants.filter(
                user__username__icontains=search
            )

        paginator = Paginator(participants, page_size)
        try:
            paginated_participants = paginator.page(page)
        except EmptyPage:
            return 400, {"error": "Page number out of range."}

        serialized_participants = [
            ParticipantSchema(
                id=participant.id,
                user_id=participant.user.id,
                exams=[ExamSchema.model_validate(exam)
                       for exam in participant.exams.all()],
                created_at=participant.created_at,
                updated_at=participant.updated_at,
            )
            for participant in paginated_participants
        ]

        return serialized_participants
    except Exception as e:
        logger.error(f"Error while listing participants: {e}")
        return 500, {"error": "An error occurred while listing participants."}


@router.get("/{participant_id}/", response={200: ParticipantSchema, 404: dict, 500: dict})
def get_participant(request, participant_id: int):
    """Retrieve a participant by ID."""
    try:
        participant = get_object_or_404(
            Participant.objects.select_related(
                "user").prefetch_related("exams"),
            id=participant_id
        )

        participant_data = ParticipantSchema(
            id=participant.id,
            user_id=participant.user.id,
            exams=[ExamSchema.model_validate(exam)
                   for exam in participant.exams.all()],
            created_at=participant.created_at,
            updated_at=participant.updated_at,
        )

        return participant_data
    except Http404:
        return 404, {"error": "Participant not found."}
    except Exception as e:
        logger.error(f"Error while retrieving participant {
                     participant_id}: {e}")
        return 500, {"error": "An error occurred while retrieving the participant."}


@router.post("/", response={201: ParticipantSchema, 400: dict, 500: dict})
def create_participant(request, data: CreateParticipantSchema):
    """Create a new participant."""
    try:
        user = get_object_or_404(User, id=data.user_id)

        if Participant.objects.filter(user=user).exists():
            return 400, {"error": "This user is already registered as a participant."}

        participant = Participant.objects.create(user=user)

        if data.exam_ids:
            exams = Exam.objects.filter(id__in=data.exam_ids)
            participant.exams.set(exams)

        participant_data = ParticipantSchema(
            id=participant.id,
            user_id=participant.user.id,
            exams=[ExamSchema.model_validate(exam)
                   for exam in participant.exams.all()],
            created_at=participant.created_at,
            updated_at=participant.updated_at,
        )

        return 201, participant_data
    except IntegrityError as e:
        logger.error(f"Integrity error while creating participant: {e}")
        return 400, {"error": "A participant with similar attributes already exists."}
    except Exception as e:
        logger.error(f"Error while creating participant: {e}")
        return 500, {"error": "An error occurred while creating the participant."}


@router.put("/{participant_id}/", response={200: ParticipantSchema, 400: dict, 404: dict, 500: dict})
def update_participant(request, participant_id: int, data: UpdateParticipantSchema):
    """Update an existing participant."""
    try:
        participant = get_object_or_404(Participant, id=participant_id)

        # Atualizar associações com provas
        if data.exam_ids:
            exams = Exam.objects.filter(id__in=data.exam_ids)
            participant.exams.set(exams)

        participant.save()

        # Retornar o participante com exames serializados
        participant_data = ParticipantSchema(
            id=participant.id,
            user_id=participant.user.id,
            exams=[ExamSchema.model_validate(exam)
                   for exam in participant.exams.all()],
            created_at=participant.created_at,
            updated_at=participant.updated_at,
        )

        return participant_data
    except Http404:
        return 404, {"error": "Participant not found."}
    except IntegrityError as e:
        logger.error(f"Integrity error while updating participant {
                     participant_id}: {e}")
        return 400, {"error": "Integrity error occurred while updating the participant."}
    except Exception as e:
        logger.error(f"Error while updating participant {participant_id}: {e}")
        return 500, {"error": "An error occurred while updating the participant."}


@router.delete("/{participant_id}/", response={200: str, 404: dict, 500: dict})
def delete_participant(request, participant_id: int):
    """Delete a participant."""
    try:
        participant = get_object_or_404(Participant, id=participant_id)
        participant.delete()
        return 200, "Participant deleted successfully."
    except Http404:
        return 404, {"error": "Participant not found."}
    except Exception as e:
        logger.error(f"Error while deleting participant {participant_id}: {e}")
        return 500, {"error": "An error occurred while deleting the participant."}
