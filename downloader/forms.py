from django import forms

class YouTubeDownloadForm(forms.Form):
    url = forms.URLField(label='YouTube URL', max_length=200)