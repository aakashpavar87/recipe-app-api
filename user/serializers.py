"""
Django User API Serializers.
"""

from datetime import timedelta

from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user object."""

    class Meta:
        model = get_user_model()
        fields = ["email", "name", "password"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        user = get_user_model().people.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        """Updating authenticated user data"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class VerifyEmailSerializer(serializers.Serializer):
    """Serializer for verify email address."""

    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get("email")
        otp = attrs.get("otp")

        try:
            user = User.people.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email address")

        if user.is_verified:
            raise serializers.ValidationError("User is already verified")

        if user.otp != otp:
            raise serializers.ValidationError("Invalid OTP")

        if timezone.now() > user.otp_creation_time + timedelta(minutes=10):
            raise serializers.ValidationError("OTP has expired")

        return attrs


class ResetOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.people.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for Token."""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(
            request=self.context.get("request"), email=email, password=password
        )
        if not user:
            msg = "Sorry unable to authenticate with given credentials."
            raise serializers.ValidationError(_(msg), code="authorization")
        attrs["user"] = user
        return attrs


class ErrorSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=255)
