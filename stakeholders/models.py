from django.db import models
from django.contrib.auth.models import User

class Stakeholder(models.Model):
    INFLUENCE_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    
    ENGAGEMENT_CHOICES = [
        ('Inform', 'Inform'),
        ('Consult', 'Consult'),
        ('Involve', 'Involve'),
        ('Collaborate', 'Collaborate'),
        ('Empower', 'Empower'),
    ]
    
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    organization = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    influence_level = models.CharField(max_length=10, choices=INFLUENCE_CHOICES, default='Medium')
    engagement_strategy = models.CharField(max_length=20, choices=ENGAGEMENT_CHOICES, default='Inform')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stakeholders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.role}"

class Engagement(models.Model):
    stakeholder = models.ForeignKey(Stakeholder, on_delete=models.CASCADE, related_name='engagements')
    date = models.DateField()
    description = models.TextField()
    outcome = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recorded_engagements')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Engagement with {self.stakeholder.name} on {self.date}"