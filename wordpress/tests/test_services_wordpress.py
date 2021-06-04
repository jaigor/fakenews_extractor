from django_mock_queries.query import MockSet
from django.test import TestCase
from mock import patch
import pytest

from wordpress.models import Wordpress
from wordpress.services import (
    TypesResponseHandler,
    ResponseHandlerError,
    WordpressRegister,
    WordpressAPI,
    NoOKResponseError,
    WordpressAlreadyExistError,
)


def create_wordpress(url, post_type, domain):
    # mock for "create_wordpress" method on the WordpressRegister model
    # to avoind touching the database.
    return Wordpress(
        url=url,
        post_type=post_type,
        domain=domain
    )


class TestTypesResponseHandler(TestCase):

    @patch.object(WordpressAPI, 'get_posts_types', side_effect=NoOKResponseError('error'))
    def test_when_wordpress_posts_not_found_raise_response_handler_error(self, mocked):
        with pytest.raises(ResponseHandlerError):
            use_case = TypesResponseHandler(
                url="www.wordpress.com/data"
            )
            use_case.handle_types_response()


@patch.object(Wordpress.objects, 'create_wordpress', side_effect=create_wordpress)  # we don't need to test django again
@patch.object(WordpressRegister, 'valid_data', return_value=None)  # already tested on TestValidData
class TestPostRegisterExecute(TestCase):
    # Test the execute method on PostRegister use case

    def setUp(self):
        # setup method will be executed on each test
        self._use_case = WordpressRegister(
            url="www.wordpress.com/data",
            post_type="Pages"
        )

    def test_return_wordpress_type(self, mock_create, mock_register):
        result = self._use_case.execute()
        assert isinstance(result, Wordpress)

    def test_create_wordpress_with_url(self, mock_create, mock_register):
        expected_result = 'www.wordpress.com/data'
        wordpress = self._use_case.execute()
        assert wordpress.url == expected_result

    def test_create_wordpress_with_post_type(self, mock_create, mock_register):
        expected_result = 'Pages'
        wordpress = self._use_case.execute()
        assert wordpress.post_type == expected_result


class TestValidData(TestCase):
    # Test the valid_data method on WordpressRegister use case
    qs_mock = MockSet(
        Wordpress(
            url="www.wordpress.com/data",
            post_type="Pages"
        )
    )

    @patch.object(Wordpress.objects, 'find_by_url', return_value=qs_mock)
    def test_when_wordpress_already_exists_raise_wordpress_already_exist_error(self, mocked):
        with pytest.raises(WordpressAlreadyExistError):
            use_case = WordpressRegister(
                url="www.wordpress.com/data",
                post_type="Pages"
            )
            use_case.valid_data()

    @patch.object(Wordpress.objects, 'find_by_url', return_value=MockSet())
    def test_when_wordpress_does_not_exists_returns_true(self, mocked):
        expected_result = True

        use_case = WordpressRegister(
            url="www.wordpress.com/data",
            post_type="Pages"
        )
        result = use_case.valid_data()
        assert result == expected_result
