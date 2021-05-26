from django import forms
from .models import Wordpress

class WordpressCreateForm(forms.ModelForm):
    url         = forms.URLField(
                        label='Website',
                        max_length=200, 
                        initial="http://",
                        widget=forms.URLInput(attrs={'class': 'form-control'}) )
                        

    class Meta:
        model = Wordpress
        fields = [
            'url'
        ]

    def clean_url(self, *args, **kwargs):
        url = self.cleaned_data.get('url')
        if not url.endswith('/'):
            url += '/'
        return url

class WordpressUpdateForm(forms.ModelForm):
    url         = forms.URLField(
                        label='Website',
                        max_length=200, 
                        initial="http://",
                        widget=forms.URLInput(attrs={'class': 'form-control'}) )
    post_type   = forms.CharField(
                        label='Tipo de Post',
                        max_length=200,
                        widget=forms.TextInput(attrs={'class': 'form-control'}) )
                        

    class Meta:
        model = Wordpress
        fields = [
            'url',
            'post_type'
        ]

    def clean_url(self, *args, **kwargs):
        url = self.cleaned_data.get('url')
        if not url.endswith('/'):
            url += '/'
        return url

    def clean_post_type(self, *args, **kwargs):
        post_type = self.cleaned_data.get('post_type')
        return post_type