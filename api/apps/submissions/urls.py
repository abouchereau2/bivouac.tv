from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "submissions"

router = DefaultRouter()
router.register("link-suggestions", views.LinkSuggestionViewSet, basename="link-suggestion")
router.register("link-reports", views.LinkReportViewSet, basename="link-report")
router.register("", views.SubmissionViewSet, basename="submission")

urlpatterns = [
    path("pending-counts/", views.pending_counts, name="pending-counts"),
    path("", include(router.urls)),
]
