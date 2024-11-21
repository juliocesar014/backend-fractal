from ninja import NinjaAPI
from django.http import JsonResponse
from api.services import calculate_exam_result
import logging

router = NinjaAPI(urls_namespace="corrections")
logger = logging.getLogger(__name__)


@router.post("/{participant_id}/exam/{exam_id}/", response={200: dict, 404: dict, 500: dict})
def trigger_correction(request, participant_id: int, exam_id: int):
    """
    Trigger automatic correction for a participant's exam.
    """
    try:
        result = calculate_exam_result(participant_id, exam_id)
        return JsonResponse(result, status=200)
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return JsonResponse({"error": str(e)}, status=404)
    except Exception as e:
        logger.error(f"Error while correcting exam: {e}")
        return JsonResponse({"error": "An internal error occurred."}, status=500)
