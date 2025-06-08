# stakeholders/forms.py

from django import forms
from .models import Stakeholder, Engagement, Tag, StakeholderRelationship, StakeholderReminder

class StakeholderForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.none(),  # This will be set in the view
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    
    class Meta:
        model = Stakeholder
        fields = ['name', 'role', 'organization', 'email', 'phone', 
                  'influence_level', 'interest_level', 'engagement_strategy', 
                  'desired_engagement', 'notes', 'tags']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'engagement_strategy': 'Current Engagement Strategy',
            'desired_engagement': 'Desired Engagement Strategy',
        }
        
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['tags'].queryset = Tag.objects.filter(created_by=user)

class EngagementForm(forms.ModelForm):
    class Meta:
        model = Engagement
        fields = [
            'stakeholder', 'date', 'description', 'outcome', 
            'communication_channel', 'follow_up_required', 
            'follow_up_date', 'satisfaction_rating'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'outcome': forms.Textarea(attrs={'rows': 3}),
            'follow_up_date': forms.DateInput(attrs={'type': 'date'}),
        }


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }


class StakeholderRelationshipForm(forms.ModelForm):
    class Meta:
        model = StakeholderRelationship
        fields = ['from_stakeholder', 'to_stakeholder', 'relationship_type', 'strength', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
        
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['from_stakeholder'].queryset = Stakeholder.objects.filter(created_by=user)
            self.fields['to_stakeholder'].queryset = Stakeholder.objects.filter(created_by=user)


class StakeholderReminderForm(forms.ModelForm):
    class Meta:
        model = StakeholderReminder
        fields = ['stakeholder', 'reminder_type', 'title', 'description', 'due_date']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['stakeholder'].queryset = Stakeholder.objects.filter(created_by=user)