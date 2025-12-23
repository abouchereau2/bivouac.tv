from rest_framework import serializers

from apps.users.serializers import UserPublicSerializer

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for reviews."""

    user = UserPublicSerializer(read_only=True)
    documentary_title = serializers.CharField(source="documentary.title", read_only=True)
    documentary_slug = serializers.CharField(source="documentary.slug", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id", "user", "documentary", "documentary_title", "documentary_slug",
            "rating", "content", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating reviews."""

    class Meta:
        model = Review
        fields = ["documentary", "rating", "content"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Check if user already reviewed this documentary (on create)."""
        request = self.context.get("request")
        if request and request.method == "POST":
            if Review.objects.filter(
                user=request.user,
                documentary=data["documentary"]
            ).exists():
                raise serializers.ValidationError(
                    "You have already reviewed this documentary."
                )
        return data
