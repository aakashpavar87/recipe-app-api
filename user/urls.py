"""
URL mappings for User API.
"""

from django.urls import path

from user import views

app_name = "user"


urlpatterns = [
    path("create/", views.CreateUserView.as_view(), name="create"),
    path("token/", views.CreateTokenView.as_view(), name="token"),
    path("verify/", views.VerifyEmailView.as_view(), name="verify-email"),
    path("reset-otp/", views.ResetOtpView.as_view(), name="reset-otp"),
    path("me/", views.ManageUserAPIView.as_view(), name="me"),
]
