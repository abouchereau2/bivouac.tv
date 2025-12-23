from django.db.models import Avg, Count
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import DocumentaryFilter
from .models import (
    Documentary,
    Person,
    Platform,
    Region,
    Sport,
    Theme,
    Watchlist,
)
from .serializers import (
    DocumentaryDetailSerializer,
    DocumentaryListSerializer,
    PersonSerializer,
    PlatformSerializer,
    RegionSerializer,
    SportSerializer,
    ThemeSerializer,
    WatchlistCreateSerializer,
    WatchlistSerializer,
)


class DocumentaryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for browsing documentaries."""

    queryset = Documentary.objects.filter(is_published=True)
    filterset_class = DocumentaryFilter
    search_fields = ["title", "original_title", "synopsis"]
    ordering_fields = ["year", "title", "created_at"]
    ordering = ["-year"]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DocumentaryDetailSerializer
        return DocumentaryListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Prefetch related for performance
        if self.action == "list":
            queryset = queryset.prefetch_related("sports")
        elif self.action == "retrieve":
            queryset = queryset.prefetch_related(
                "sports", "themes", "regions", "directors",
                "availabilities__platform"
            )

        return queryset

    @action(detail=False, methods=["get"])
    def featured(self, request):
        """Get featured documentaries."""
        queryset = self.get_queryset().filter(is_featured=True)[:10]
        serializer = DocumentaryListSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def top_rated(self, request):
        """Get top-rated documentaries."""
        queryset = (
            self.get_queryset()
            .annotate(avg_rating=Avg("reviews__rating"), review_count=Count("reviews"))
            .filter(review_count__gte=3)
            .order_by("-avg_rating")[:10]
        )
        serializer = DocumentaryListSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def recent(self, request):
        """Get recently added documentaries."""
        queryset = self.get_queryset().order_by("-created_at")[:10]
        serializer = DocumentaryListSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def add_to_watchlist(self, request, slug=None):
        """Add documentary to user's watchlist."""
        documentary = self.get_object()
        watchlist, created = Watchlist.objects.get_or_create(
            user=request.user, documentary=documentary
        )
        if created:
            return Response({"status": "added"}, status=status.HTTP_201_CREATED)
        return Response({"status": "already in watchlist"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["delete"], permission_classes=[permissions.IsAuthenticated])
    def remove_from_watchlist(self, request, slug=None):
        """Remove documentary from user's watchlist."""
        documentary = self.get_object()
        deleted, _ = Watchlist.objects.filter(
            user=request.user, documentary=documentary
        ).delete()
        if deleted:
            return Response({"status": "removed"}, status=status.HTTP_200_OK)
        return Response({"status": "not in watchlist"}, status=status.HTTP_404_NOT_FOUND)


class WatchlistViewSet(viewsets.ModelViewSet):
    """ViewSet for user's watchlist."""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user).select_related(
            "documentary"
        ).prefetch_related("documentary__sports")

    def get_serializer_class(self):
        if self.action == "create":
            return WatchlistCreateSerializer
        return WatchlistSerializer


class SportListView(generics.ListAPIView):
    """List all sports."""

    queryset = Sport.objects.all()
    serializer_class = SportSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class ThemeListView(generics.ListAPIView):
    """List all themes."""

    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class RegionListView(generics.ListAPIView):
    """List all regions."""

    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class PlatformListView(generics.ListAPIView):
    """List all platforms."""

    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class PersonListView(generics.ListAPIView):
    """List all people (directors, etc.)."""

    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = [permissions.AllowAny]
    search_fields = ["name"]
