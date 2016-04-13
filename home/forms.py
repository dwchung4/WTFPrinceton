from django import forms
from django.contrib.auth.models import User

from .models import Petition


class PetitionForm(forms.ModelForm):

    class Meta:
        model = Petition
        widgets = {
          'content': forms.Textarea(attrs={'rows':'14','cols':'50','style':'resize:none'}),
        }
        fields = ['title', 'category', 'content']