from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from .models import Review
from .serializers import ReviewCreateSerializer, ReviewSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow owners to edit, others to read only."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for reviews."""

    queryset = Review.objects.select_related("user", "documentary")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filterset_fields = ["documentary", "user", "rating"]
    ordering_fields = ["created_at", "rating"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by documentary slug if provided
        documentary_slug = self.request.query_params.get("documentary_slug")
        if documentary_slug:
            queryset = queryset.filter(documentary__slug=documentary_slug)

        return queryset

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You can only edit your own reviews.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You can only delete your own reviews.")
        instance.delete()
