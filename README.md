# Django Authentication API

An authentication backend built with Django REST Framework, Simple JWT, and a custom user model. The project provides a clean API for user registration, email verification, login, JWT refresh, logout with token blacklisting, profile access, and password reset flows.

## Overview

This project focuses on a practical authentication system with production-oriented patterns:

- Custom user model based on `AbstractUser`
- UUID primary keys for users
- JWT-based authentication
- Email verification after registration
- Password reset via email token links
- Profile endpoint for authenticated users
- Strong password validation rules
- HTML Email template 

## Tech Stack

- Django
- Django REST Framework
- djangorestframework-simplejwt
- SQLite for local development
- SMTP email delivery
- Django templates for verification and reset emails


## Core Features

### Authentication

- Register a new account with username, email, first name, last name, and password confirmation
- Log in with username and password
- Refresh access tokens using Simple JWT
- Log out by blacklisting refresh tokens

### Account Security

- Email verification required before login
- Password reset request and confirmation flow
- Custom password validator enforcing complexity requirements
- Unique username and email validation

### User Profile

- Authenticated profile retrieval
- Extended user model fields:
  - Featured image
  - Phone number
  - Address
  - Verification status
  - Join and update timestamps


## Project Structure

```text
auth/
├── manage.py
├── db.sqlite3
├── README.md
├── apps/
│   └── users/
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       ├── utils.py
│       ├── validators.py
│       └── templates/users/
└── config/
    ├── settings.py
    ├── urls.py
    ├── asgi.py
    └── wsgi.py
```

## Authentication Flow

1. A user registers with email and password.
2. The system sends a verification email containing a tokenized link.
3. The user verifies the account through the link.
4. The user can then log in and receive JWT access and refresh tokens.
5. Protected endpoints require a valid access token.
6. Refresh tokens can be rotated and blacklisted after logout.

## API Endpoints

Base path: `/api/v1/`

### Register

- `POST /api/v1/register/`

Example payload:

```json
{
  "username": "john.doe",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "password": "StrongPass@123",
  "confirm_password": "StrongPass@123"
}
```

### Login

- `POST /api/v1/login/`

Example payload:

```json
{
  "username": "john.doe",
  "password": "StrongPass@123"
}
```

### Profile

- `GET /api/v1/profile/`

Requires authentication with a JWT access token.

### Logout

- `POST /api/v1/logout/`

Requires authentication and the refresh token in the request body.

### Refresh Token

- `POST /api/v1/refresh/`

Provided by Simple JWT.

### Request Password Reset

- `POST /api/v1/password-reset-request/`

Example payload:

```json
{
  "email": "john@example.com"
}
```

### Confirm Password Reset Token

- `GET /api/v1/password-reset-token-confirm/<uidb64>/<token>/`

### Reset Password

- `POST /api/v1/password-reset-confirm/`

Example payload:

```json
{
  "uidb64": "encoded-user-id",
  "token": "token-from-email",
  "new_password": "NewStrongPass@123",
  "confirm_new_password": "NewStrongPass@123"
}
```

### Verify Email

- `GET /api/v1/verify-email/<uidb64>/<token>/`

## Validation Rules

The project uses layered validation to keep accounts secure:

- Username must be unique, 3 to 10 characters, and may contain letters, numbers, dots, underscores, and hyphens
- Email must be unique
- Passwords must match during registration and reset
- Passwords must include letters, digits, and special characters
- Password must satisfy Django's built-in validators as well

## Environment Variables

Create a `.env` file in the project root with the following values:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=your-email@example.com
```

## Local Setup

1. Create and activate a virtual environment.
2. Install the dependencies.
3. Run migrations.
4. Start the development server.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Next Improvements

- Add automated tests for registration, login, verification, and password reset
- Add API documentation with Swagger or ReDoc
- Add frontend integration examples
- Support deployment-specific email and CORS settings through environment variables
