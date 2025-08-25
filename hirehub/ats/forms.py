# hirehub/ats/forms.py
from django import forms
from .models import Applicant, JobPosition

class JobPositionForm(forms.ModelForm):
    class Meta:
        model = JobPosition
        fields = ['title', 'description', 'requirements', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = [
            'name', 'email', 'phone', 'job_position', 'source',
            'resume_file', 'tags'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'job_position': forms.Select(attrs={'class': 'form-control'}),
            'source': forms.Select(attrs={'class': 'form-control'}),
            'resume_file': forms.FileInput(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., JavaScript, Senior, Remote'}),
        }
        help_texts = {
            'tags': 'Separate tags with commas',
            'resume_file': 'Accepted formats: PDF, DOC, DOCX',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the empty label for the 'source' and 'job_position' dropdowns
        if 'source' in self.fields:
            self.fields['source'].choices = [('', 'Select Source')] + list(self.fields['source'].choices)[1:]

        if 'job_position' in self.fields:
            self.fields['job_position'].queryset = JobPosition.objects.filter(is_active=True)
            self.fields['job_position'].empty_label = "Select Job Position"
