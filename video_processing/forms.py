from django import forms
from .models import ProcessedVideo

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = ProcessedVideo
        fields = ('title', 'video')
