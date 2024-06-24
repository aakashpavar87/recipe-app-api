"""
Views For User API.
"""

from rest_framework import generics

from user import serializers


class CreateUserView(generics.CreateAPIView):
    """Creating User in the system."""

    serializer_class = serializers.UserSerializer
