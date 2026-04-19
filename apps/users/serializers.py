from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import MaxLengthValidator, MinLengthValidator, RegexValidator
from rest_framework.validators import UniqueValidator
from apps.users.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.permissions import AllowAny
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str



class UserRegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.-]+$',
                message='Username can only contain letters, numbers, dots, underscores, and hyphens.'
            ),
            UniqueValidator(queryset=User.objects.all(), message="This username is already taken."),
            MaxLengthValidator(10),
            MinLengthValidator(3),
        ],
    )
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all(), message="This email is already registered.")
        ],
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )

    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta : 
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'confirm_password']    

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match.", "confirm_password": "Passwords do not match."})

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user



class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)
        data['user'] = user
        
        if not user:
            raise serializers.ValidationError({"username": "Invalid username or password.", "password": "Invalid username or password."})
        elif not user.is_verified:
            raise serializers.ValidationError("This account is not validated yet.")
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        read_only_fields = ['username', 'email']



class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)



class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        try : 
            user = User.objects.get(email=attrs.get("email"))
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "No user is associated with this email address."})
        
        if not user.is_verified :
            raise serializers.ValidationError("This account is not validated yet.")
        attrs['user'] = user
        return attrs



class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    uidb64 = serializers.CharField(required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password], style={'input_type': 'password'})
    confirm_new_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})


    def validate(self, data):
        try : 
            uid = force_str(urlsafe_base64_decode(data["uidb64"]))
            user = User.objects.get(id=uid)
            token = PasswordResetTokenGenerator().check_token(user, data["token"])
            if not token:
                raise serializers.ValidationError({"token": "Invalid or expired token."})
        except : 
            raise serializers.ValidationError({"token": "Invalid or expired token."})

        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({"new_password": "Passwords do not match.", "confirm_new_password": "Passwords do not match."})
        
        data["user"] = user
        return data
    