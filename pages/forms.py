from django import forms

# methods
METHODS = (
    ("", "No método"),
    ("BERT", "BERT")
)


class ClassifierForm(forms.Form):

    def __init__(self, tweets, *args, **kwarg):
        super().__init__(*args, **kwarg)
        if tweets is not None:
            self.fields['tweets'].label = 'Tweets a escoger'
            self.fields['tweets'].widget = forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
            self.fields['tweets'].choices = tweets

    method = forms.ChoiceField(
        label='Modelo a usar',
        choices=METHODS,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    tweets = forms.MultipleChoiceField(
    )

    class Meta:
        fields = [
            'method',
            'tweets',
        ]

    def clean_method(self):
        return self.cleaned_data.get('method')

    def clean_tweets(self):
        return self.cleaned_data.get('tweets')