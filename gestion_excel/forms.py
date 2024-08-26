# myapp/forms.py
from django import forms
from .models import DynamicData

class UploadFileForm(forms.Form):
    file = forms.FileField()

class DynamicDataForm(forms.ModelForm):
    class Meta:
        model = DynamicData
        fields = '__all__' 