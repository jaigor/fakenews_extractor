from django import forms
from .models import Query, Tweet


class QueryCreateForm(forms.ModelForm):

    text = forms.CharField(
        label='Texto a buscar',
        max_length=512,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Query
        fields = [
            'text'
        ]

    def clean_query(self):
        return self.cleaned_data.get('text')


TRUE_FALSE = (
    (True, "True"),
    (False, "False")
)


class TweetUpdateForm(forms.ModelForm):

    text = forms.CharField(
        label='Texto del tweet',
        max_length=512,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    created_at = forms.CharField(
        label='Creado en',
        max_length=512,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    lang = forms.CharField(
        label='Idioma',
        max_length=120,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    spreader = forms.BooleanField(
        label='Difunde',
        required=False,
        widget=forms.RadioSelect(choices=TRUE_FALSE, attrs={'class': 'form-check-input', 'type': 'radio'}))

    percentage = forms.FloatField(
        label='Porcentaje',
        widget=forms.NumberInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Tweet
        fields = [
            'text',
            'created_at',
            'lang',
            'spreader',
            'percentage',
        ]