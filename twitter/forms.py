from django import forms
from .models import Tweet, User, Query

class QueryCreateForm(forms.ModelForm):
    query   = forms.CharField(
                        label='Texto a buscar',   
                        max_length=120,
                        widget=forms.TextInput(attrs={'class': 'form-control'}) )

    class Meta:
        model = Query
        fields = [
            'query'
        ]

    def clean_url(self, *args, **kwargs):
        return self.cleaned_data.get('query')

