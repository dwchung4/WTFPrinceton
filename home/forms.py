from django import forms
from django.contrib.auth.models import User
from .models import Greeting

class GreetingForm(forms.ModelForm):

	class Meta:
		model = Greeting
		fields = ['artist']