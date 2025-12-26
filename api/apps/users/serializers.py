from rest_framework import serializers

from .models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""

    favorite_sports = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = ["avatar", "bio", "favorite_sports", "created_at"]
        read_only_fields = ["created_at"]


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details."""

    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "username", "first_name", "last_name", "is_staff", "profile", "date_joined"]
        read_only_fields = ["id", "email", "is_staff", "date_joined"]


class UserPublicSerializer(serializers.ModelSerializer):
    """Serializer for public user information (used in reviews, etc.)."""

    avatar = serializers.ImageField(source="profile.avatar", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "avatar"]
        read_only_fields = fields
