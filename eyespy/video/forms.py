from .models import Video
from django import forms


class Video_form(forms.ModelForm):

    class Meta:
        model = Video
        fields = ("title","video")