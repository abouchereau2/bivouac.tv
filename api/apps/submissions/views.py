from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Submission
from .serializers import (
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
        """Approve a submission (admin only)."""
        submission = self.get_object()
        if submission.status != Submission.Status.PENDING:
            return Response(
                {"error": "Can only approve pending submissions"},
                status=status.HTTP_400_BAD_REQUEST
            )

        submission.status = Submission.Status.APPROVED
        submission.reviewed_by = request.user
        submission.reviewed_at = timezone.now()
        submission.review_notes = request.data.get("notes", "")
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
