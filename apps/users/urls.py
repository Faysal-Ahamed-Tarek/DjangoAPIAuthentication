from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView



urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("password-reset-request/", views.passwordResetRequestView.as_view(), name="password_reset_request"),
    path("password-reset-confirm/", views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("password-reset-token-confirm/<str:uidb64>/<str:token>/", views.passwordResetTokenConfirmView.as_view(), name="password_reset_token_confirm"),
    path("verify-email/<str:uidb64>/<str:token>/", views.VerifyEmailView.as_view(), name="verify_email"),
]