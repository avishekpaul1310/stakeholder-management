# stakeholders/forms.py
from django import forms
from .models import Stakeholder

class StakeholderForm(forms.ModelForm):
    class Meta:
        model = Stakeholder
        fields = ['name', 'email', 'role', 'organization', 'phone', 'notes', 'power', 'interest', 'current_engagement_level', 'desired_engagement_level']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.TextInput(attrs={'class': 'form-control'}),
            'organization': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'power': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10}),
            'interest': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10}),
            'current_engagement_level': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 5}),
            'desired_engagement_level': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 5}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove any non-digit characters
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) < 10:
                raise forms.ValidationError("Please enter a valid phone number with at least 10 digits")
        return phone