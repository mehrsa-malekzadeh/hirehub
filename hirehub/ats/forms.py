# hirehub/ats/forms.py
from django import forms
from .models import Applicant

class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = [
            'name', 'email', 'phone', 'source',
            'resume_file', 'tags'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
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
        # The 'source' field in the Applicant model is a CharField with choices and blank=True.
        # When Django creates a form field for such a model field, if it's not required (due to blank=True),
        # it automatically prepends an empty choice, which typically looks like ('', '---------').
        # This __init__ method customizes this behavior for the 'source' field.
        # It replaces Django's default empty choice label with "Select Source".

        # Convert current choices to a list to safely manipulate them.
        current_choices_list = list(self.fields['source'].choices)

        if current_choices_list and current_choices_list[0][0] == '':
            # If the first choice is Django's default empty choice (value is an empty string),
            # replace it with our custom "Select Source" label while keeping the empty value.
            self.fields['source'].choices = [('', 'Select Source')] + current_choices_list[1:]
        else:
            # If there was no empty choice prepended by Django (e.g., if the field was required,
            # or if choices were already customized), or if the choices list was empty,
            # we prepend our "Select Source" option. This case is less likely for a field
            # with blank=True but ensures robustness.
            self.fields['source'].choices = [('', 'Select Source')] + current_choices_list
