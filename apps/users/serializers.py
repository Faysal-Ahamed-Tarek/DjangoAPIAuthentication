from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import MaxLengthValidator, MinLengthValidator, RegexValidator
from rest_framework.validators import UniqueValidator
from apps.users.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate


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
        elif not user.is_active:
            raise serializers.ValidationError("This account is not validated yet.")
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_verified']
        read_only_fields = ['username', 'email', 'is_verified']


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)
    access = serializers.CharField(required=True)

