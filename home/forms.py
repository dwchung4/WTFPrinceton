from django import forms
from django.contrib.auth.models import User

from .models import Petition


class PetitionForm(forms.ModelForm):

    class Meta:
        model = Petition
        fields = ['title', 'category', 'content']