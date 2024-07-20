from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Task

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'wake_up_time', 'sleep_time', 'productive_hours', 'preferred_categories',
            'study_duration', 'study_environment', 'major', 'year_of_study',
            'recurring_commitments', 'learning_style', 'short_term_goals', 'long_term_goals'
        ]

class TaskForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea, label='Task Description')
