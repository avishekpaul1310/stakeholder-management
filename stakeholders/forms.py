from django import forms
from .models import Stakeholder

class StakeholderForm(forms.ModelForm):
    class Meta:
        model = Stakeholder
        fields = ['name', 'email', 'role', 'organization', 'phone', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
        }