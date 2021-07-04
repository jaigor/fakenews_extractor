from django import forms
from .models import Query


class QueryCreateForm(forms.ModelForm):

    query = forms.CharField(
        label='Texto a buscar',
        max_length=512,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Query
        fields = [
            'query'
        ]

    def clean_query(self):
        return self.cleaned_data.get('query')
