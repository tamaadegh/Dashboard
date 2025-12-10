from django.conf import settings
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate
from allauth.account import app_settings as allauth_settings
from allauth.account.utils import complete_signup
from allauth.account.models import EmailAddress

from nxtbn.users.api.storefront.serializers import (
    JwtBasicUserSerializer,
    LoginRequestSerializer,
    RefreshSerializer,
    SignupSerializer,
)
from nxtbn.users.utils.jwt_utils import JWTManager


class SignupView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    authentication_classes = []
    serializer_class = SignupSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.jwt_manager = JWTManager()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        complete_signup(request._request, user, allauth_settings.EMAIL_VERIFICATION, None)

        response_data = {"detail": _("Verification e-mail sent. Please check your email.")}

        if allauth_settings.EMAIL_VERIFICATION != allauth_settings.EmailVerificationMethod.MANDATORY:
            access_token = self.jwt_manager.generate_access_token(user)
            refresh_token = self.jwt_manager.generate_refresh_token(user)

            user_data = JwtBasicUserSerializer(user).data
            response_data = {
                "user": user_data,
                "token": {
                    "access": access_token,
                    "refresh": refresh_token,
                    "expires_in": self.jwt_manager.access_token_expiration_seconds,
                    "refresh_expires_in": self.jwt_manager.refresh_token_expiration_seconds,
                },
            }

        response = Response(response_data, status=status.HTTP_201_CREATED)
        response.set_cookie(
            key=self.jwt_manager.access_token_cookie_name,
            value=access_token,
            httponly=True,  # Make in-accessible via JavaScript (recommended)
            secure=True,
            samesite="None",  # Options: 'Strict', 'Lax', 'None'
            max_age=self.jwt_manager.access_token_expiration,
        )
        response.set_cookie(
            key=self.jwt_manager.refresh_token_cookie_name,
            value=refresh_token,
            httponly=True,  # Make in-accessible via JavaScript (recommended)
            secure=True,
            samesite="None",  # Options: 'Strict', 'Lax', 'None'
            max_age=self.jwt_manager.refresh_token_expiration,
        )
        return response



class LogoutView(APIView):
    permission_classes = (AllowAny,)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.jwt_manager = JWTManager()

    def post(self, request):
        """
        Logout the user by clearing the JWT cookies.
        """
        response = Response({"detail": _("Logged out successfully.")}, status=status.HTTP_200_OK)

        # Clear the JWT cookies
        response.delete_cookie(self.jwt_manager.access_token_cookie_name)
        response.delete_cookie(self.jwt_manager.refresh_token_cookie_name)

        # Optional: Revoke the refresh token if your JWTManager supports revocation
        refresh_token = request.COOKIES.get(self.jwt_manager.refresh_token_cookie_name)
        if refresh_token:
            self.jwt_manager.revoke_refresh_token(refresh_token)

        return response