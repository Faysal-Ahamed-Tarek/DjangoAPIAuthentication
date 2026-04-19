from rest_framework.response import Response
from apps.users.serializers import UserRegistrationSerializer
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import AllowAny
from apps.users.utils import send_verification_email, send_password_reset_email
from .models import User
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserLoginSerializer,
    LogoutSerializer,
    UserProfileSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from datetime import timedelta

class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        send_verification_email(user, self.request)
        return Response(
            {
                "message": "Registration successful. Please check your email to verify your account.",
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            user_id = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(id=user_id)

            if PasswordResetTokenGenerator().check_token(user, token):
                if not user.is_verified:
                    user.is_verified = True
                    user.save()
                else:
                    return Response(
                        {"message": "Email is already verified."},
                        status=status.HTTP_200_OK,
                    )
            else:
                return Response(
                    {"error": "Invalid or expired token."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Email verified successfully."}, status=status.HTTP_200_OK
        )


class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        
        return Response(
            {
                "message": "Login successful.",
                "user": {
                    "username": user.username,
                    "email": user.email,
                    "is_verified": user.is_verified,
                },
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh"]
        try:
            refresh_token = RefreshToken(refresh_token)
            refresh_token.blacklist()
        except TokenError:
            return Response(
                {"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)


class passwordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        send_password_reset_email(user, request)

        return Response(
            {"message": "Password reset email sent. Please check your inbox."},
            status=status.HTTP_200_OK,
        )


class passwordResetTokenConfirmView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try : 
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=uid)
            token = PasswordResetTokenGenerator().check_token(user, token)
            if not token:
                return Response(
                    {"error": "Invalid or expired token."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except : 
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {
                "message": "Token is valid. You can now reset your password.",
                "token": token,
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password = serializer.validated_data["new_password"]
        user = serializer.validated_data["user"]
        user.set_password(password)
        user.save(update_fields=["password"])

        return Response(
            {"message": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )