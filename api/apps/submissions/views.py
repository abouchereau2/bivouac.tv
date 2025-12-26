from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes as perm_classes
from rest_framework.response import Response

from .models import LinkReport, LinkSuggestion, Submission


@api_view(["GET"])
@perm_classes([permissions.IsAdminUser])
def pending_counts(request):
    """Get counts of all pending items for admin dashboard badge."""
    submissions = Submission.objects.filter(status=Submission.Status.PENDING).count()
    suggestions = LinkSuggestion.objects.filter(status=LinkSuggestion.Status.PENDING).count()
    reports = LinkReport.objects.filter(status=LinkReport.Status.PENDING).count()
    return Response({
        "submissions": submissions,
        "suggestions": suggestions,
        "reports": reports,
        "total": submissions + suggestions + reports,
    })
from .serializers import (
    LinkReportCreateSerializer,
    LinkReportSerializer,
    LinkSuggestionCreateSerializer,
    LinkSuggestionSerializer,
    SubmissionAdminSerializer,
    SubmissionCreateSerializer,
    SubmissionSerializer,
)


class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow owners to view their submissions, admins to view all."""

    def has_object_permission(self, request, view, obj):
        return obj.submitted_by == request.user or request.user.is_staff


class SubmissionViewSet(viewsets.ModelViewSet):
    """ViewSet for submissions."""

    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filterset_fields = ["status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Submission.objects.all()
        return Submission.objects.filter(submitted_by=user)

    def get_serializer_class(self):
        if self.action == "create":
            return SubmissionCreateSerializer
        if self.request.user.is_staff:
            return SubmissionAdminSerializer
        return SubmissionSerializer

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        """Approve a submission and create a placeholder documentary (admin only)."""
        from apps.documentaries.models import Documentary

        submission = self.get_object()
        if submission.status != Submission.Status.PENDING:
            return Response(
                {"error": "Can only approve pending submissions"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create a placeholder documentary (unpublished by default)
        documentary = Documentary.objects.create(
            title=submission.title,
            year=submission.year,
            duration_minutes=90,  # Default placeholder value
            is_published=False,  # Not published until admin completes it
        )

        submission.status = Submission.Status.APPROVED
        submission.reviewed_by = request.user
        submission.reviewed_at = timezone.now()
        submission.review_notes = request.data.get("notes", "")
        submission.created_documentary = documentary
        submission.save()

        return Response(SubmissionAdminSerializer(submission).data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        """Reject a submission (admin only)."""
        submission = self.get_object()
        if submission.status != Submission.Status.PENDING:
            return Response(
                {"error": "Can only reject pending submissions"},
                status=status.HTTP_400_BAD_REQUEST
            )

        submission.status = Submission.Status.REJECTED
        submission.reviewed_by = request.user
        submission.reviewed_at = timezone.now()
        submission.review_notes = request.data.get("notes", "")
        submission.save()

        return Response(SubmissionAdminSerializer(submission).data)

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAdminUser])
    def pending(self, request):
        """Get all pending submissions (admin only)."""
        queryset = Submission.objects.filter(status=Submission.Status.PENDING)
        serializer = SubmissionAdminSerializer(queryset, many=True)
        return Response(serializer.data)


class LinkSuggestionViewSet(viewsets.ModelViewSet):
    """ViewSet for link suggestions."""

    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status", "documentary"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return LinkSuggestion.objects.select_related("platform", "submitted_by").all()
        return LinkSuggestion.objects.select_related("platform", "submitted_by").filter(
            submitted_by=user
        )

    def get_serializer_class(self):
        if self.action == "create":
            return LinkSuggestionCreateSerializer
        return LinkSuggestionSerializer

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        """Approve a link suggestion and create the availability."""
        from apps.documentaries.models import Availability

        suggestion = self.get_object()
        if suggestion.status != LinkSuggestion.Status.PENDING:
            return Response(
                {"error": "Can only approve pending suggestions"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the availability
        Availability.objects.update_or_create(
            documentary=suggestion.documentary,
            platform=suggestion.platform,
            defaults={
                "url": suggestion.url,
                "is_free": suggestion.is_free,
            }
        )

        suggestion.status = LinkSuggestion.Status.APPROVED
        suggestion.reviewed_by = request.user
        suggestion.reviewed_at = timezone.now()
        suggestion.review_notes = request.data.get("notes", "")
        suggestion.save()

        return Response(LinkSuggestionSerializer(suggestion).data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        """Reject a link suggestion."""
        suggestion = self.get_object()
        if suggestion.status != LinkSuggestion.Status.PENDING:
            return Response(
                {"error": "Can only reject pending suggestions"},
                status=status.HTTP_400_BAD_REQUEST
            )

        suggestion.status = LinkSuggestion.Status.REJECTED
        suggestion.reviewed_by = request.user
        suggestion.reviewed_at = timezone.now()
        suggestion.review_notes = request.data.get("notes", "")
        suggestion.save()

        return Response(LinkSuggestionSerializer(suggestion).data)

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAdminUser])
    def pending(self, request):
        """Get all pending link suggestions (admin only)."""
        queryset = LinkSuggestion.objects.filter(
            status=LinkSuggestion.Status.PENDING
        ).select_related("platform", "submitted_by", "documentary")
        serializer = LinkSuggestionSerializer(queryset, many=True)
        return Response(serializer.data)


class LinkReportViewSet(viewsets.ModelViewSet):
    """ViewSet for link reports."""

    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status", "reason"]
    ordering = ["-created_at"]
    http_method_names = ["get", "post", "head", "options"]  # No update/delete for users

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return LinkReport.objects.select_related("reported_by", "availability").all()
        return LinkReport.objects.select_related("reported_by", "availability").filter(
            reported_by=user
        )

    def get_serializer_class(self):
        if self.action == "create":
            return LinkReportCreateSerializer
        return LinkReportSerializer

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def fix(self, request, pk=None):
        """Mark a report as fixed and delete the broken availability link."""
        report = self.get_object()
        if report.status != LinkReport.Status.PENDING:
            return Response(
                {"error": "Can only fix pending reports"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Store availability for deletion and clear the FK first
        # (to avoid integrity errors when deleting cascades back)
        availability = report.availability

        # Update the report first, clearing the availability FK
        report.availability = None
        report.status = LinkReport.Status.FIXED
        report.resolved_by = request.user
        report.resolved_at = timezone.now()
        report.resolution_notes = request.data.get("notes", "")
        report.save()

        # Now delete the broken availability link
        if availability:
            availability.delete()

        return Response(LinkReportSerializer(report).data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def dismiss(self, request, pk=None):
        """Dismiss a report."""
        report = self.get_object()
        if report.status != LinkReport.Status.PENDING:
            return Response(
                {"error": "Can only dismiss pending reports"},
                status=status.HTTP_400_BAD_REQUEST
            )

        report.status = LinkReport.Status.DISMISSED
        report.resolved_by = request.user
        report.resolved_at = timezone.now()
        report.resolution_notes = request.data.get("notes", "")
        report.save()

        return Response(LinkReportSerializer(report).data)

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAdminUser])
    def pending(self, request):
        """Get all pending link reports (admin only)."""
        queryset = LinkReport.objects.filter(
            status=LinkReport.Status.PENDING
        ).select_related("reported_by", "availability__platform", "availability__documentary")
        serializer = LinkReportSerializer(queryset, many=True)
        return Response(serializer.data)
