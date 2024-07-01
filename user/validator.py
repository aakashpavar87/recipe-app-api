"""
Middlewares for processing user per request.
"""

from django.contrib.auth import authenticate, get_user_model
from django.http import HttpResponseForbidden, JsonResponse
from rest_framework import status
from rest_framework.response import Response

"""
Syntax For middlewares
class Class_Name:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # * Before Calling view
        # ! Do some thing before request executes
        response = self.get_response(request)
        # * After calling view
        # ! Do some thing after request executes
        return response
"""


def check_is_verified(user):
    """Check that user is verified or not."""
    if not user.is_verified:
        return {
            "message": "User is not verified. Please verify your account and try again."
        }
