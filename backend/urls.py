from django.contrib import admin
from django.urls import path
from api.api import router


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", router.urls),
]