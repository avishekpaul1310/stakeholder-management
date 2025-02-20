from django.db import models
from django.contrib.auth.models import AbstractUser

class Stakeholder(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    role = models.CharField(max_length=100)
    organization = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    power = models.IntegerField(default=0)  # 0 to 10 scale
    interest = models.IntegerField(default=0)  # 0 to 10 scale
    current_engagement_level = models.IntegerField(default=0)  # 0 to 5 scale
    desired_engagement_level = models.IntegerField(default=0)  # 0 to 5 scale
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

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

    class Meta:
        permissions = [
            ("view_dashboard", "Can view dashboard"),
            ("view_reports", "Can view reports"),
        ]