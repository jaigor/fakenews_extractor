from django import forms
from .models import Query


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
