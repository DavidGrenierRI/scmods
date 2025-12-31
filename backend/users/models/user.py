# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    initials = models.CharField(
        max_length=3,
        blank=True,
        help_text="3-character initials for display next to tasks"
    )
    
    class Meta:
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return self.get_full_name() or self.username