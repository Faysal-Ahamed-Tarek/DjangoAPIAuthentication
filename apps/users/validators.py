import re
from django.core.exceptions import ValidationError


class PasswordValidator:
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password) and not re.search(r'[a-z]', password) :
            raise ValidationError("Password must contain at least one letter.")
        if not re.search(r'[0-9]', password):
            raise ValidationError("Password must contain at least one digit.")
        if not re.search(r'[@$!%*?&]', password):
            raise ValidationError("Password must contain at least one special character (@, $, !, %, *, ?, &).")

    def get_help_text(self):
        return "Your password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character (@, $, !, %, *, ?, &)."