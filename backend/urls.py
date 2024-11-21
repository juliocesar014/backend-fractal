from django.contrib import admin
from django.urls import path
from api.api_user import router as user_router
from api.api_exam import router as exam_router

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", user_router.urls),
    path("api/exams/", exam_router.urls),
]
