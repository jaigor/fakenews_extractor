from django import forms
from .models import Soup

# iterable 
ATTR_CHOICES =( 
    ("1", "Id"), 
    ("2", "Class")
)

class SoupCreateForm(forms.ModelForm):
    url         = forms.URLField(
                        label='URL Colección',
                        max_length=120, 
                        initial="http://",
                        widget=forms.URLInput(attrs={'class': 'form-control'}) )
    link_class  = forms.CharField(
                        label='Clase Link',   
                        max_length=120,
                        widget=forms.TextInput(attrs={'class': 'form-control'}) )
    date_type   = forms.ChoiceField(
                        label='Tipo Fecha',
                        choices = ATTR_CHOICES,
                        widget=forms.Select(attrs={'class': 'form-select'}) )
    date_id     = forms.CharField(
                        label='Atributo Fecha',
                        max_length=120,
                        widget=forms.TextInput(attrs={'class': 'form-control'}) )   

    class Meta:
        model = Soup
        fields = [
            'url',
            'link_class',
            'date_type',
            'date_id'
        ]

    def clean_url(self, *args, **kwargs):
        return self.cleaned_data.get('url')

    def clean_link_class(self, *args, **kwargs):
        return self.cleaned_data.get('link_class')

    def clean_date_type(self, *args, **kwargs):
        return self.cleaned_data.get('date_type')

    def clean_date_id(self, *args, **kwargs):
        return self.cleaned_data.get('date_id')
