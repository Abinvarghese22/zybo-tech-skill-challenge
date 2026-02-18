"""
Custom User Model for the Chat Application.
Extends AbstractUser to include online status tracking.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    """
    Custom User Model with required fields:
    - email (unique)
    - username
    - password (inherited from AbstractUser)
    - is_online (BooleanField)
    - last_seen (DateTimeField)
    """
    email = models.EmailField(unique=True, verbose_name='Email Address')
    is_online = models.BooleanField(default=False, verbose_name='Online Status')
    last_seen = models.DateTimeField(default=timezone.now, verbose_name='Last Seen')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username']

    def __str__(self):
        return self.username
