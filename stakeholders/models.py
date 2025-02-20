from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    ADMIN = 'admin'
    VIEWER = 'viewer'
    
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (VIEWER, 'Viewer'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=VIEWER,
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class Stakeholder(models.Model):
    name = models.CharField(max_length=200)
    organization = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    email = models.EmailField()
    power = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 11)],
        help_text="Rate from 1-10"
    )
    interest = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 11)],
        help_text="Rate from 1-10"
    )
    current_engagement_level = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Rate from 1-5"
    )
    desired_engagement_level = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Rate from 1-5"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name