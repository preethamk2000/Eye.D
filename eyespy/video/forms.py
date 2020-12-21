from .models import Video
from django import forms


class Video_form(forms.ModelForm):

    class Meta:
        model = Video
        fields = ("title","video")
        widgets = {'frames': forms.HiddenInput(),
                   'fps': forms.HiddenInput() }