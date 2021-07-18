from django import forms
from .base_models import FakeNews

# iterables
LINK_CHOICES = (
    ("1", "Pattern"),
    ("2", "Class")
)
YES_NO = (
    (True, "Sí"),
    (False, "No")
)


class FakeNewsForm(forms.ModelForm):

    url = forms.URLField(
        label='Website',
        max_length=200,
        initial="http://",
        widget=forms.URLInput(attrs={'class': 'form-control'}))

    # first url
    f_source_type = forms.ChoiceField(
        label='Tipo Enlace',
        choices=LINK_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}))
    f_source_pattern = forms.CharField(
        label='Patrón de búsqueda del enlace (para ocurrencias de 0 o más caracteres incluir {*})',
        max_length=256,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    f_source_entire_link = forms.BooleanField(
        label='Coger enlace completo',
        required=False,
        widget=forms.RadioSelect(choices=YES_NO, attrs={'class': 'form-check-input', 'type': 'radio'}))

    # second
    s_source_type = forms.ChoiceField(
        label='Tipo Enlace',
        choices=LINK_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}))
    s_source_pattern = forms.CharField(
        label='Patrón de búsqueda del enlace (para ocurrencias de 0 o más caracteres incluir {*})',
        max_length=256,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    s_source_entire_link = forms.BooleanField(
        label='Coger enlace completo',
        required=False,
        widget=forms.RadioSelect(choices=YES_NO, attrs={'class': 'form-check-input', 'type': 'radio'}))

    class Meta:
        model = FakeNews
        fields = '__all__'
