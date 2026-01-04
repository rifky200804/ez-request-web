from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator

class User(AbstractUser):
    """
    Custom User model with relaxed username validation.
    """
    # Override username to allow spaces and other characters if desired, 
    # though AbstractUser's default is already fairly permissive for Unicode.
    # To truly allow "any" character, we can remove the validator or use a custom one.
    # Here we stick to standard but ensure it's explicit, or we can just pass blank validators.
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[], # Remove default validators to allow "freedom of characters"
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
