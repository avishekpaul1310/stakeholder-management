from django import forms
from .models import Stakeholder, Engagement

class StakeholderForm(forms.ModelForm):
    class Meta:
        model = Stakeholder
        fields = ['name', 'role', 'organization', 'email', 'phone', 
                  'influence_level', 'interest_level', 'engagement_strategy', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

class EngagementForm(forms.ModelForm):
    class Meta:
        model = Engagement
        fields = ['stakeholder', 'date', 'description', 'outcome']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'outcome': forms.Textarea(attrs={'rows': 3}),
        }