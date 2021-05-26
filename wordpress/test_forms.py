from django.test import TestCase
from .forms import WordpressCreateForm, WordpressUpdateForm

class TestForms(TestCase):

    def test_create_when_all_fields_are_filled_up_and_the_form_is_valid(self):
        data = {
            'url': 'https://www.snopes.com/'
        }

        form = WordpressCreateForm(data=data)
        assert form.is_valid() is True

    def test_update_when_post_type_is_empty_returns_error(self):
        data = {
            'url': 'https://www.snopes.com/',
            'post_type': None
        }

        form = WordpressUpdateForm(data=data)
        assert 'post_type' in form.errors

    def test_update_when_all_fields_are_filled_up_and_the_form_is_valid(self):
        data = {
            'url': 'https://www.snopes.com/',
            'post_type': 'posts'
        }

        form = WordpressUpdateForm(data=data)
        assert form.is_valid() is True