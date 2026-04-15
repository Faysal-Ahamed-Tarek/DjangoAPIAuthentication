import token

from rest_framework.response import Response
from apps.users.serializers import UserRegistrationSerializer
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import AllowAny
from apps.users.utils import send_verification_email
from .models import User
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .serializers import UserLoginSerializer, LogoutSerializer, UserProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_verification_email(user, request)
        return Response(
            {
                "message": "Registration successful. Please check your email to verify your account."
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            user = User.objects.get(id=user_id)

            if not user.is_verified:
                user.is_verified = True
                user.save()
            else : 
                return Response(
                    {"message": "Email is already verified."}, status=status.HTTP_200_OK
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
        if user.is_verified == False:
            return Response(
                {"error": "This account is not validated yet."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
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
        access_token = serializer.validated_data["access"]
        try:
            refresh_token = RefreshToken(refresh_token)
            refresh_token.blacklist()

        except TokenError:
            return Response(
                {"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)
