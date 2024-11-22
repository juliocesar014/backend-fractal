from ninja import NinjaAPI, Query
from api.models import Result, Exam
from django.db.models import F
from django.core.paginator import Paginator, EmptyPage
from typing import Optional
import logging
from ninja.decorators import decorate_view
from django.views.decorators.cache import cache_page

router = NinjaAPI(urls_namespace="rankings")
logger = logging.getLogger(__name__)


@router.get("/{exam_id}/", response={200: list[dict], 400: dict, 404: dict, 500: dict})
@decorate_view(cache_page(60*15))
def get_ranking(
    request,
    exam_id: int,
    order: Optional[str] = Query("rank"),
    page: int = Query(1),
    page_size: int = Query(10),
):
    """
    Get the ranking for an exam with optional ordering and pagination.
    """
    try:
        exam = Exam.objects.get(id=exam_id)

        order_fields = {
            "rank": "-score",
            "username": "username",
            "score": "-score",
        }

        if order not in order_fields:
            return 400, {"error": f"Invalid order field. Allowed: {', '.join(order_fields.keys())}"}

        results = (
            Result.objects.filter(exam=exam)
            .annotate(username=F("participant__user__username"))
            .values("username", "score", "max_score", "created_at")
            .order_by(order_fields[order], "created_at")
        )

        paginator = Paginator(results, page_size)
        try:
            paginated_results = paginator.page(page)
        except EmptyPage:
            return 400, {"error": "Page number out of range."}

        ranking = []
        for rank, result in enumerate(paginated_results, start=(page - 1) * page_size + 1):
            ranking.append({
                "rank": rank,
                "username": result["username"],
                "score": result["score"],
                "max_score": result["max_score"],
                "percentage": round((result["score"] / result["max_score"]) * 100, 2),
            })

        return ranking
    except Exam.DoesNotExist:
        return 404, {"error": "Exam not found."}
    except Exception as e:
        logger.error(f"Error while calculating ranking for exam {
                     exam_id}: {e}")
        return 500, {"error": "An error occurred while calculating the ranking."}
