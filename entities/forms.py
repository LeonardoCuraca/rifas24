from django import forms
from django.contrib.auth.forms import UserCreationForm

from entities.models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'appearance-none rounded-lg block w-full px-4 py-3 border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary transition-all'}),
            'last_name': forms.TextInput(attrs={'class': 'appearance-none rounded-lg block w-full px-4 py-3 border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary transition-all'}),
            'email': forms.EmailInput(attrs={'class': 'appearance-none rounded-lg block w-full px-4 py-3 border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary transition-all'}),
            'phone': forms.TextInput(attrs={'class': 'appearance-none rounded-lg block w-full px-4 py-3 border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary transition-all'}),
        }