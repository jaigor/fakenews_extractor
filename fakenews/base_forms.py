from django import forms
from .base_models import FakeNews


class FakeNewsForm(forms.ModelForm):

    url = forms.URLField(
        label='Website',
        max_length=200,
        initial="http://",
        widget=forms.URLInput(attrs={'class': 'form-control'}))

    class Meta:
        model = FakeNews
        fields = [
            'url'
        ]
