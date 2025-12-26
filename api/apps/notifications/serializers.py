from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications."""

    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_type",
            "status",
            "title",
            "message",
            "read",
            "read_at",
            "created_at",
            "documentary_title",
            "documentary_slug",
            "documentary_poster",
        ]
        read_only_fields = [
            "id",
            "notification_type",
            "status",
            "title",
            "message",
            "created_at",
            "documentary_title",
            "documentary_slug",
            "documentary_poster",
        ]
