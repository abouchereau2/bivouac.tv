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


class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = ["id", "name", "slug", "icon"]


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = ["id", "name", "slug"]


class RegionSerializer(serializers.ModelSerializer):
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
