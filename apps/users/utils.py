from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes



def send_verification_email(user, request):
    token = PasswordResetTokenGenerator().make_token(user)
    verification_path = reverse('verify_email', kwargs={'uidb64': urlsafe_base64_encode(force_bytes(user.pk)), 'token': token})
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

    token = PasswordResetTokenGenerator().make_token(user)
    url = request.build_absolute_uri(
        reverse("password_reset_token_confirm", kwargs={"uidb64": urlsafe_base64_encode(force_bytes(user.pk)), "token": str(token)})
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