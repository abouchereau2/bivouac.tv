from rest_framework import serializers

from .models import (
    Availability,
    Documentary,
    Person,
    Platform,
    Region,
    Sport,
    Theme,
    Watched,
    Watchlist,
)


def get_request_language(context):
    """Get language from request context."""
    request = context.get("request")
    if request:
        # Try Accept-Language header first
        accept_lang = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
        if accept_lang:
            return accept_lang[:2]
        # Fall back to LANGUAGE_CODE or 'en'
        return getattr(request, "LANGUAGE_CODE", "en")[:2]
    return "en"


class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = ["id", "name_en", "name_fr", "slug", "icon"]


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = ["id", "name_en", "name_fr", "slug"]


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ["id", "name_en", "name_fr", "slug"]


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
    is_watched = serializers.SerializerMethodField()

    class Meta:
        model = Documentary
        fields = [
            "id", "title", "slug", "year", "duration_minutes",
            "poster", "sports", "average_rating", "review_count",
            "is_in_watchlist", "is_watched"
        ]

    def get_is_in_watchlist(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Watchlist.objects.filter(
                user=request.user, documentary=obj
            ).exists()
        return False

    def get_is_watched(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Watched.objects.filter(
                user=request.user, documentary=obj
            ).exists()
        return False


class DocumentaryHeroSerializer(serializers.ModelSerializer):
    """Serializer for hero section (backdrop + synopsis + minimal metadata)."""

    sports = SportSerializer(many=True, read_only=True)
    themes = ThemeSerializer(many=True, read_only=True)
    synopsis = serializers.SerializerMethodField()
    average_rating = serializers.ReadOnlyField()

    class Meta:
        model = Documentary
        fields = [
            "id", "title", "slug", "year", "duration_minutes",
            "synopsis", "backdrop", "poster", "sports", "themes", "average_rating"
        ]

    def get_synopsis(self, obj):
        """Return synopsis based on request language preference."""
        lang = get_request_language(self.context)
        return obj.get_synopsis(lang)


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
    is_watched = serializers.SerializerMethodField()
    synopsis = serializers.SerializerMethodField()

    class Meta:
        model = Documentary
        fields = [
            "id", "title", "original_title", "slug", "year", "duration_minutes",
            "synopsis", "poster", "backdrop", "trailer_url",
            "directors", "sports", "themes", "regions",
            "imdb_id", "imdb_rating", "tmdb_id",
            "availabilities", "average_rating", "review_count",
            "is_in_watchlist", "is_watched", "created_at", "updated_at"
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

    def get_is_watched(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Watched.objects.filter(
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


class WatchedSerializer(serializers.ModelSerializer):
    documentary = DocumentaryListSerializer(read_only=True)

    class Meta:
        model = Watched
        fields = ["id", "documentary", "watched_at"]


class WatchedCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watched
        fields = ["documentary"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
