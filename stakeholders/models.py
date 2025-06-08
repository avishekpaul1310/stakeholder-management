# stakeholders/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Tag(models.Model):
    """Tags for categorizing stakeholders"""
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tags')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

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
    tags = models.ManyToManyField(Tag, blank=True)
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
    COMMUNICATION_CHANNELS = [
        ('email', 'Email'),
        ('phone', 'Phone Call'),
        ('meeting', 'In-Person Meeting'),
        ('video', 'Video Call'),
        ('informal', 'Informal Chat'),
        ('presentation', 'Presentation'),
        ('workshop', 'Workshop'),
        ('survey', 'Survey'),
    ]
    
    stakeholder = models.ForeignKey(Stakeholder, on_delete=models.CASCADE, related_name='engagements')
    date = models.DateField()
    description = models.TextField()
    outcome = models.TextField(blank=True)
    communication_channel = models.CharField(max_length=50, choices=COMMUNICATION_CHANNELS, default='email')
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_completed = models.BooleanField(default=False)
    satisfaction_rating = models.IntegerField(
        choices=[(1, '1 - Poor'), (2, '2 - Fair'), (3, '3 - Good'), (4, '4 - Very Good'), (5, '5 - Excellent')],
        null=True, blank=True
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recorded_engagements')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Engagement with {self.stakeholder.name} on {self.date}"
    
    class Meta:
        ordering = ['-date']

class StakeholderRelationship(models.Model):
    """Represents relationships between stakeholders"""
    RELATIONSHIP_TYPES = [
        ('reports_to', 'Reports To'),
        ('colleagues', 'Colleagues'),
        ('influences', 'Influences'),
        ('collaborates', 'Collaborates With'),
        ('supervises', 'Supervises'),
        ('partner', 'Business Partner'),
        ('competitor', 'Competitor'),
        ('dependent', 'Dependent On'),
    ]
    
    from_stakeholder = models.ForeignKey(Stakeholder, on_delete=models.CASCADE, related_name='relationships_from')
    to_stakeholder = models.ForeignKey(Stakeholder, on_delete=models.CASCADE, related_name='relationships_to')
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_TYPES)
    strength = models.IntegerField(choices=[(1, 'Weak'), (2, 'Medium'), (3, 'Strong')], default=2)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_relationships')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.from_stakeholder.name} {self.get_relationship_type_display()} {self.to_stakeholder.name}"
    
    class Meta:
        unique_together = ['from_stakeholder', 'to_stakeholder', 'relationship_type']


class Activity(models.Model):
    """Activity feed for tracking all stakeholder-related actions"""
    ACTIVITY_TYPES = [
        ('created', 'Stakeholder Created'),
        ('updated', 'Stakeholder Updated'),
        ('engagement', 'Engagement Recorded'),
        ('deleted', 'Stakeholder Deleted'),
        ('relationship_added', 'Relationship Added'),
        ('tag_added', 'Tag Added'),
        ('tag_removed', 'Tag Removed'),
        ('ai_insight', 'AI Insight Generated'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    stakeholder_name = models.CharField(max_length=100)
    stakeholder_id = models.IntegerField(null=True, blank=True)  # May be null if stakeholder is deleted
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} - {self.stakeholder_name}"
    
    class Meta:
        ordering = ['-timestamp']


class StakeholderInsight(models.Model):
    """AI-generated insights for stakeholders"""
    stakeholder = models.ForeignKey(Stakeholder, on_delete=models.CASCADE, related_name='insights')
    insight_text = models.TextField()
    confidence_score = models.FloatField(default=0.0)  # 0.0 to 1.0
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_helpful = models.BooleanField(null=True, blank=True)  # User feedback
    
    def __str__(self):
        return f"Insight for {self.stakeholder.name} - {self.created_at.strftime('%Y-%m-%d')}"
    
    class Meta:
        ordering = ['-created_at']


class StakeholderReminder(models.Model):
    """Reminders for stakeholder follow-ups"""
    REMINDER_TYPES = [
        ('follow_up', 'Follow-up Engagement'),
        ('review', 'Stakeholder Review'),
        ('update', 'Information Update'),
        ('meeting', 'Scheduled Meeting'),
    ]
    
    stakeholder = models.ForeignKey(Stakeholder, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPES, default='follow_up')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_reminders')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Reminder: {self.title} for {self.stakeholder.name}"
    
    def mark_completed(self):
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save()
    
    class Meta:
        ordering = ['due_date']