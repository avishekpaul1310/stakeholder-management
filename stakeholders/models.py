# stakeholders/models.py

from django.db import models

class Stakeholder(models.Model):
    ROLE_CHOICES = [
        ('SPONSOR', 'Sponsor'),
        ('VENDOR', 'Vendor'),
        ('TEAM_MEMBER', 'Team Member'),
    ]

    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name