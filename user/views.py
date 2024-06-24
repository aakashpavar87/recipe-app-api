"""
Views For User API.
"""

from rest_framework import authentication, generics, permissions
from rest_framework.authtoken.views import ObtainAuthToken

from user.serializers import AuthTokenSerializer, UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Creating User in the system."""

    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Creating Authentication Token For User."""

    serializer_class = AuthTokenSerializer


class ManageUserAPIView(generics.RetrieveUpdateAPIView):
    """Retrieve and Update API View."""

    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
