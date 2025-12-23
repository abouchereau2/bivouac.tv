import django_filters

from .models import Documentary


class DocumentaryFilter(django_filters.FilterSet):
    """Filter for documentaries."""

    # Text search
    search = django_filters.CharFilter(method="filter_search")

    # Range filters
    year_min = django_filters.NumberFilter(field_name="year", lookup_expr="gte")
    year_max = django_filters.NumberFilter(field_name="year", lookup_expr="lte")
    duration_min = django_filters.NumberFilter(field_name="duration_minutes", lookup_expr="gte")
    duration_max = django_filters.NumberFilter(field_name="duration_minutes", lookup_expr="lte")

    # Relation filters (accept slugs)
    sport = django_filters.CharFilter(field_name="sports__slug")
    theme = django_filters.CharFilter(field_name="themes__slug")
    region = django_filters.CharFilter(field_name="regions__slug")
    director = django_filters.CharFilter(field_name="directors__slug")

    # Platform filter (accept slug)
    platform = django_filters.CharFilter(field_name="availabilities__platform__slug")

    # Free content filter
    is_free = django_filters.BooleanFilter(field_name="availabilities__is_free")

    # Featured filter
    is_featured = django_filters.BooleanFilter()

    class Meta:
        model = Documentary
        fields = [
            "search", "year_min", "year_max", "duration_min", "duration_max",
            "sport", "theme", "region", "director", "platform", "is_free",
            "is_featured"
        ]

    def filter_search(self, queryset, name, value):
        """Search in title, original_title, and synopsis."""
        return queryset.filter(
            models.Q(title__icontains=value) |
            models.Q(original_title__icontains=value) |
            models.Q(synopsis__icontains=value)
        )


# Import models for Q lookup
from django.db import models  # noqa: E402
