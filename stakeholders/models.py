# stakeholders/models.py

from django.db import models
from django.contrib.auth.models import User

class Stakeholder(models.Model):
    INFLUENCE_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    
    INTEREST_CHOICES = [
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
    interest_level = models.CharField(max_length=10, choices=INTEREST_CHOICES, default='Medium')
    engagement_strategy = models.CharField(max_length=20, choices=ENGAGEMENT_CHOICES, default='Inform')
    desired_engagement = models.CharField(max_length=20, choices=ENGAGEMENT_CHOICES, default='Inform')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stakeholders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.role}"
    
    def get_engagement_level_value(self):
        engagement_values = {
            'Inform': 1,
            'Consult': 2,
            'Involve': 3,
            'Collaborate': 4,
            'Empower': 5
        }
        return engagement_values.get(self.engagement_strategy, 1)

    def get_desired_engagement_level_value(self):
        engagement_values = {
            'Inform': 1,
            'Consult': 2,
            'Involve': 3,
            'Collaborate': 4,
            'Empower': 5
        }
        return engagement_values.get(self.desired_engagement, 1)
    
    def get_influence_value(self):
        influence_values = {
            'Low': 25,
            'Medium': 50,
            'High': 75
        }
        return influence_values.get(self.influence_level, 50)

    def get_interest_value(self):
        interest_values = {
            'Low': 25,
            'Medium': 50,
            'High': 75
        }
        return interest_values.get(self.interest_level, 50)
    
    def get_quadrant(self):
        if self.get_influence_value() >= 50 and self.get_interest_value() >= 50:
            return "Manage Closely"
        elif self.get_influence_value() >= 50 and self.get_interest_value() < 50:
            return "Keep Satisfied"
        elif self.get_influence_value() < 50 and self.get_interest_value() >= 50:
            return "Keep Informed"
        else:
            return "Monitor"
    
class Engagement(models.Model):
    stakeholder = models.ForeignKey(Stakeholder, on_delete=models.CASCADE, related_name='engagements')
    date = models.DateField()
    description = models.TextField()
    outcome = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recorded_engagements')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Engagement with {self.stakeholder.name} on {self.date}"