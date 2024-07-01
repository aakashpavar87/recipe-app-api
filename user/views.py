"""
Views For User API.
"""

import secrets
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model, login, logout
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import authentication, generics, permissions, status, views
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from user.mailer import send_email_to_customer
from user.serializers import (
    AuthTokenSerializer,
    ErrorSerializer,
    ResetOtpSerializer,
    UserSerializer,
    VerifyEmailSerializer,
)
from user.validator import check_is_verified

User = get_user_model()


# # create mail object
# mail = mt.Mail(
#     sender=mt.Address(email="mailtrap@example.com", name="Mailtrap Test"),
#     to=[mt.Address(email="your@email.com")],
#     subject="You are awesome!",
#     text="Congrats for sending test email with Mailtrap!",
# )

# # create client and send
# client = mt.MailtrapClient(token="c8bf2cdcec499f0c82e1f1b49de97fd2")
# client.send(mail)


class CreateUserView(generics.CreateAPIView):
    """Creating User in the system."""

    serializer_class = UserSerializer

    def perform_create(self, serializer):

        created_otp = secrets.randbelow(900000) + 100000
        email = serializer.validated_data.get("email")
        send_email_to_customer(
            [email],
            "Email Verification",
            f"Dear, Customer Please verify your email address with this code {created_otp}",
        )
        serializer.save(otp=f"{created_otp}", otp_creation_time=datetime.now())


class VerifyEmailView(generics.GenericAPIView):
    """View for verifying email."""

    serializer_class = VerifyEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = self.perform_verification(serializer)
        except ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"message": "Email verified successfully"}, status=status.HTTP_200_OK
        )

    def perform_verification(self, serializer):
        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:
            user = User.people.get(email=email)
        except User.DoesNotExist:
            raise ValidationError("Invalid email address")

        if user.is_verified:
            raise ValidationError("User is already verified")

        if user.otp != otp:
            raise ValidationError("Invalid OTP")

        if timezone.now() > user.otp_creation_time + timedelta(minutes=10):
            raise ValidationError("OTP has expired")

        user.is_verified = True
        user.otp = None
        user.otp_creation_time = None
        user.save()
        return user


class ResetOtpView(generics.GenericAPIView):
    serializer_class = ResetOtpSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.people.get(email=email)
            user.otp = secrets.randbelow(900000) + 100000
            send_email_to_customer(
                [email],
                "Email Verification",
                f"Dear, Customer Please verify your email address with this new code {user.otp}",
            )
            user.otp_creation_time = datetime.now()
            user.save()
        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "OTP has been reset and sent to your email."},
            status=status.HTTP_200_OK,
        )


class CreateTokenView(ObtainAuthToken):
    """Creating Authentication Token For User."""

    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        print(f"From User Views : {user}")
        request.session["user_id"] = user.id

        return Response(
            {
                "token": token.key,
                "user_id": user.id,
                "email": user.email,
                "message": _("Login successful"),
            },
            status=status.HTTP_200_OK,
        )


class ManageUserAPIView(generics.RetrieveUpdateAPIView):
    """Retrieve and Update API View."""

    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        # Check if user is verified
        response = check_is_verified(user)
        if response:
            self.serializer_class = ErrorSerializer
            return response
        return user
