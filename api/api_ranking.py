from ninja import NinjaAPI
from api.models import Result, Exam
from django.db.models import F
import logging

router = NinjaAPI(urls_namespace="rankings")
logger = logging.getLogger(__name__)


@router.get("/{exam_id}/", response={200: list[dict], 404: dict, 500: dict})
def get_ranking(request, exam_id: int):
    """
    Get the ranking for an exam.
    """
    try:
        exam = Exam.objects.get(id=exam_id)

        results = (
            Result.objects.filter(exam=exam)
            .annotate(username=F("participant__user__username"))
            .values("username", "score", "max_score")
            .order_by("-score", "created_at")
        )

        ranking = []
        for rank, result in enumerate(results, start=1):
            ranking.append({
                "rank": rank,
                "username": result["username"],
                "score": result["score"],
                "max_score": result["max_score"],
                "percentage": round((result["score"] / result["max_score"]) * 100, 2)
            })

        return ranking
    except Exam.DoesNotExist:
        return 404, {"error": "Exam not found."}
    except Exception as e:
        logger.error(f"Error while calculating ranking for exam {
                     exam_id}: {e}")
        return 500, {"error": "An error occurred while calculating the ranking."}
