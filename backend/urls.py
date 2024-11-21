from django.contrib import admin
from django.urls import path
from api.api_user import router as user_router
from api.api_exam import router as exam_router
from api.api_question import router as question_router
from api.api_choice import router as choice_router
from api.api_participants import router as participant_router
from api.api_answer import router as answer_router

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", user_router.urls),
    path("api/exams/", exam_router.urls),
    path("api/questions/", question_router.urls),
    path("api/choices/", choice_router.urls),
    path("api/participants/", participant_router.urls),
    path("api/answers/", answer_router.urls),
]
