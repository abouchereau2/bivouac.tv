from rest_framework import serializers

from apps.documentaries.serializers import PlatformSerializer
from apps.users.serializers import UserPublicSerializer

from .models import LinkReport, LinkSuggestion, Submission


class SubmissionSerializer(serializers.ModelSerializer):
    """Serializer for submissions."""

    submitted_by = UserPublicSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = [
            "id", "submitted_by", "title", "year", "url", "notes",
            "status", "created_at"
        ]
        read_only_fields = ["id", "submitted_by", "status", "created_at"]


class SubmissionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating submissions."""

    class Meta:
        model = Submission
        fields = ["title", "year", "url", "notes"]

    def create(self, validated_data):
        validated_data["submitted_by"] = self.context["request"].user
        return super().create(validated_data)


class SubmissionAdminSerializer(serializers.ModelSerializer):
    """Serializer for admin actions on submissions."""

    submitted_by = UserPublicSerializer(read_only=True)
    reviewed_by = UserPublicSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = [
            "id", "submitted_by", "title", "year", "url", "notes",
            "status", "reviewed_by", "review_notes", "reviewed_at",
            "created_documentary", "created_at", "updated_at"
        ]
        read_only_fields = [
            "id", "submitted_by", "title", "year", "url", "notes",
            "reviewed_by", "reviewed_at", "created_at", "updated_at"
        ]


# Link Suggestion Serializers

class LinkSuggestionSerializer(serializers.ModelSerializer):
    """Serializer for link suggestions."""

    platform = PlatformSerializer(read_only=True)
    submitted_by = UserPublicSerializer(read_only=True)
    documentary_title = serializers.CharField(source="documentary.title", read_only=True)
    documentary_slug = serializers.CharField(source="documentary.slug", read_only=True)

    class Meta:
        model = LinkSuggestion
        fields = [
            "id", "documentary", "documentary_title", "documentary_slug",
            "platform", "url", "is_free", "notes",
            "submitted_by", "status", "created_at"
        ]
        read_only_fields = ["id", "documentary", "submitted_by", "status", "created_at"]


class LinkSuggestionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating link suggestions."""

    class Meta:
        model = LinkSuggestion
        fields = ["documentary", "platform", "url", "is_free", "notes"]

    def create(self, validated_data):
        validated_data["submitted_by"] = self.context["request"].user
        return super().create(validated_data)


# Link Report Serializers

class LinkReportSerializer(serializers.ModelSerializer):
    """Serializer for link reports."""

    reported_by = UserPublicSerializer(read_only=True)
    # Use denormalized fields, with fallback to availability for backwards compat
    documentary_title = serializers.SerializerMethodField()
    documentary_slug = serializers.SerializerMethodField()
    platform_name = serializers.SerializerMethodField()
    availability_url = serializers.CharField(source="availability.url", read_only=True)

    class Meta:
        model = LinkReport
        fields = [
            "id", "availability", "documentary_title", "documentary_slug",
            "platform_name", "availability_url", "reason", "details",
            "reported_by", "status", "created_at"
        ]
        read_only_fields = ["id", "reported_by", "status", "created_at"]

    def get_documentary_title(self, obj):
        # Use denormalized field first, fallback to availability
        if obj.documentary_title:
            return obj.documentary_title
        if obj.availability and obj.availability.documentary:
            return obj.availability.documentary.title
        return None

    def get_documentary_slug(self, obj):
        if obj.documentary_slug:
            return obj.documentary_slug
        if obj.availability and obj.availability.documentary:
            return obj.availability.documentary.slug
        return None

    def get_platform_name(self, obj):
        if obj.platform_name:
            return obj.platform_name
        if obj.availability and obj.availability.platform:
            return obj.availability.platform.name
        return None


class LinkReportCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating link reports."""

    class Meta:
        model = LinkReport
        fields = ["availability", "reason", "details"]

    def create(self, validated_data):
        validated_data["reported_by"] = self.context["request"].user
        # Denormalize documentary info at creation time
        availability = validated_data.get("availability")
        if availability:
            if availability.documentary:
                validated_data["documentary_title"] = availability.documentary.title
                validated_data["documentary_slug"] = availability.documentary.slug
            if availability.platform:
                validated_data["platform_name"] = availability.platform.name
        return super().create(validated_data)
