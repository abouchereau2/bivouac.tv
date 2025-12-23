from rest_framework import serializers

from .models import (
    Availability,
    Documentary,
    Person,
    Platform,
    Region,
    Sport,
    Theme,
    Watchlist,
)


def get_request_language(context):
    """Get language from request context."""
    request = context.get("request")
    if request:
        # Try query_params (DRF request) or GET (Django request)
        query_params = getattr(request, "query_params", None) or getattr(request, "GET", {})
        lang = query_params.get("lang") or getattr(request, "LANGUAGE_CODE", "en")
        return lang[:2] if lang else "en"
    return "en"


class I18nNameMixin:
    """Mixin to add language-aware name field."""

    def get_name(self, obj):
        lang = get_request_language(self.context)
        return obj.get_name(lang)


class SportSerializer(I18nNameMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Sport
        fields = ["id", "name", "slug", "icon"]


class ThemeSerializer(I18nNameMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Theme
        fields = ["id", "name", "slug"]


class RegionSerializer(I18nNameMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ["id", "name", "slug"]


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ["id", "name", "slug", "photo"]


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ["id", "name", "slug", "logo", "website", "is_free"]


class AvailabilitySerializer(serializers.ModelSerializer):
    platform = PlatformSerializer(read_only=True)

    class Meta:
        model = Availability
        fields = [
            "id", "platform", "url", "is_free",
            "available_from", "available_until", "country_codes"
        ]


class DocumentaryListSerializer(serializers.ModelSerializer):
    """Serializer for documentary list view (minimal data)."""

    sports = SportSerializer(many=True, read_only=True)
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    is_in_watchlist = serializers.SerializerMethodField()

    class Meta:
        model = Documentary
        fields = [
            "id", "title", "slug", "year", "duration_minutes",
            "poster", "sports", "average_rating", "review_count",
            "is_in_watchlist"
        ]

    def get_is_in_watchlist(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Watchlist.objects.filter(
                user=request.user, documentary=obj
            ).exists()
        return False


class DocumentaryDetailSerializer(serializers.ModelSerializer):
    """Serializer for documentary detail view (full data)."""

    sports = SportSerializer(many=True, read_only=True)
    themes = ThemeSerializer(many=True, read_only=True)
    regions = RegionSerializer(many=True, read_only=True)
    directors = PersonSerializer(many=True, read_only=True)
    availabilities = AvailabilitySerializer(many=True, read_only=True)
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    is_in_watchlist = serializers.SerializerMethodField()
    synopsis = serializers.SerializerMethodField()

    class Meta:
        model = Documentary
        fields = [
            "id", "title", "original_title", "slug", "year", "duration_minutes",
            "synopsis", "poster", "backdrop", "trailer_url",
            "directors", "sports", "themes", "regions",
            "imdb_id", "imdb_rating", "tmdb_id",
            "availabilities", "average_rating", "review_count",
            "is_in_watchlist", "created_at", "updated_at"
        ]

    def get_synopsis(self, obj):
        """Return synopsis based on request language preference."""
        lang = get_request_language(self.context)
        return obj.get_synopsis(lang)

    def get_is_in_watchlist(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Watchlist.objects.filter(
                user=request.user, documentary=obj
            ).exists()
        return False


class WatchlistSerializer(serializers.ModelSerializer):
    documentary = DocumentaryListSerializer(read_only=True)

    class Meta:
        model = Watchlist
        fields = ["id", "documentary", "added_at"]


class WatchlistCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watchlist
        fields = ["documentary"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
