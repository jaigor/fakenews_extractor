from django import forms
from .models import Wordpress, Soup
from .base_forms import FakeNewsForm


class WordpressCreateForm(FakeNewsForm):
    class Meta(FakeNewsForm.Meta):
        model = Wordpress
        fields = [
            'url'
        ]

    def clean_url(self):
        url = self.cleaned_data.get('url')
        if not url.endswith('/'):
            url += '/'
        return url


class WordpressUpdateForm(FakeNewsForm):

    post_type = forms.CharField(
        label='Tipo de Post',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta(FakeNewsForm.Meta):
        model = Wordpress
        fields = [
            'url',
            'post_type'
        ]

    def clean_url(self):
        url = self.cleaned_data.get('url')
        if not url.endswith('/'):
            url += '/'
        return url

    def clean_post_type(self):
        post_type = self.cleaned_data.get('post_type')
        return post_type


# iterable
ATTR_CHOICES = (
    ("1", "Id"),
    ("2", "Class")
)


class SoupCreateForm(FakeNewsForm):
    link_class = forms.CharField(
        label='Clase Link',
        max_length=120,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    date_type = forms.ChoiceField(
        label='Tipo Fecha',
        choices=ATTR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}))
    date_id = forms.CharField(
        label='Atributo Fecha',
        max_length=120,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    body_class = forms.CharField(
        label='Clase Cuerpo',
        max_length=120,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Soup
        fields = [
            'url',
            'link_class',
            'date_type',
            'date_id',
            'body_class'
        ]

    def clean_link_class(self):
        return self.cleaned_data.get('link_class')

    def clean_date_type(self):
        return self.cleaned_data.get('date_type')

    def clean_date_id(self):
        return self.cleaned_data.get('date_id')

    def clean_body_class(self):
        return self.cleaned_data.get('body_class')
