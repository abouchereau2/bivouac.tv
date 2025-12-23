from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "submissions"

router = DefaultRouter()
router.register("", views.SubmissionViewSet, basename="submission")

urlpatterns = [
    path("", include(router.urls)),
]
