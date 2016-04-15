from django import forms
from django.contrib.auth.models import User

from .models import Petition


class PetitionForm(forms.ModelForm):

    class Meta:
        model = Petition

        # Set the size of content textbox
        widgets = {
          'content': forms.Textarea(attrs={'rows':'16','cols':'45','style':'resize:none'}),
        }
        
        fields = ['title', 'category', 'content']