from django.test import TestCase
from .forms import SoupCreateForm

class TestForms(TestCase):

    def test_create_when_all_fields_are_filled_up_and_the_form_is_valid(self):
        data = {
            'url': 'https://www.snopes.com/',
            'link_class': 'class',
            'date_type': "1",
            'date_id': 'dateid'
        }

        form = SoupCreateForm(data=data)
        assert form.is_valid() is True

    def test_create_when_date_id_is_empty_returns_error(self):
        data = {
            'url': 'https://www.snopes.com/',
            'date_id': None
        }

        form = SoupCreateForm(data=data)
        assert 'date_type' in form.errors

    def test_create_when_date_type_is_wrong_format_returns_error(self):
        data = {
            'url': 'https://www.snopes.com/',
            'link_class': 'class',
            'date_type': 'a',
            'date_id': 'dateid'
        }

        form = SoupCreateForm(data=data)
        assert 'date_type' in form.errors