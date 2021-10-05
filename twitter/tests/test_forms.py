from django.test import TestCase

from twitter.forms import QueryCreateForm


class TestTwitterForms(TestCase):

    def test_query_with_no_text_throw_error(self):
        data = {
            'text': ''
        }

        form = QueryCreateForm(data=data)
        assert 'text' in form.errors

    def test_create_filled_up_and_the_form_is_valid(self):
        data = {
            'text': 'Test'
        }

        form = QueryCreateForm(data=data)
        assert form.is_valid() is True
