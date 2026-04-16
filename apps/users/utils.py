from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .models import User



def send_verification_email(user, request):
    refresh_token = RefreshToken.for_user(user)
    access_token = str(refresh_token.access_token)
    verification_path = reverse('verify_email', kwargs={'token': access_token})
    verification_link = request.build_absolute_uri(verification_path)
    
    context = {
        'user': user,
        'verification_url': verification_link,
        'site_name': 'Your App Name',
    }

    subject = 'Verify Your Email Address'
    html_message = render_to_string('users/verification_email.html', context)
    message = strip_tags(html_message)

    send_mail(
        subject,
        message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )



def send_password_reset_email(user, request):

    token = AccessToken.for_user(user)
    token["password_reset"] = True

    url = request.build_absolute_uri(
        reverse("password_reset_token_confirm", kwargs={"token": str(token)})
    )

    context = {
        'user': user,
        'reset_url': url,
        'site_name': 'Your App Name',
    }

    subject = 'Password Reset Request'
    html_message = render_to_string('users/password_reset_email.html', context)
    message = strip_tags(html_message)

    send_mail(
        subject,
        message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )