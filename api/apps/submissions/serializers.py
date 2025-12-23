from rest_framework import serializers

from apps.users.serializers import UserPublicSerializer

from .models import Submission


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
