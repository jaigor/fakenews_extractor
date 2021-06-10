from django_mock_queries.query import MockSet
from django.test import TestCase
from mock import patch
import pytest

from fakenews.models import Wordpress, Post
from fakenews.register import WordpressRegister, SoupRegister
from fakenews.base_register import PostRegister, PostAlreadyExistError

from fakenews.tasks import WordpressAlreadyExistError


def create_wordpress(url, post_type, domain):
    # mock for "create_wordpress" method on the WordpressRegister model
    # to avoid touching the database.
    return Wordpress(
        url=url,
        post_type=post_type,
        domain=domain
    )


class TestWordpressValidData(TestCase):
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


@patch.object(Wordpress.objects, 'create_wordpress', side_effect=create_wordpress)  # we don't need to test django again
@patch.object(WordpressRegister, 'valid_data', return_value=None)  # already tested on TestValidData
class TestWordpressRegisterExecute(TestCase):
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


# POST #
def create_post(link, date, title, content):
    # mock for "create_post" method on the PostRegister model
    # to avoid touching the database.
    return Post(
        link=link,
        date=date,
        title=title,
        content=content
    )


class TestPostValidData(TestCase):
    # Test the valid_data method on PostRegister use case
    qs_mock = MockSet(
        Post(
            link="www.wordpress.com/posts/1",
            date="01/01/2021",
            title="Post",
            content="Post Content"
        )
    )

    @patch.object(Post.objects, 'find_by_link', return_value=qs_mock)
    def test_when_post_already_exists_raise_post_already_exist_error(self, mocked):
        with pytest.raises(PostAlreadyExistError):
            use_case = PostRegister(
                "www.wordpress.com/posts/1",
                "01/01/2021",
                "Post",
                "Post Content"
            )
            use_case.valid_data()

    @patch.object(Post.objects, 'find_by_link', return_value=MockSet())
    def test_when_post_does_not_exists_returns_true(self, mocked):
        expected_result = True

        use_case = PostRegister(
            "www.wordpress.com/posts/1",
            "01/01/2021",
            "Post",
            "Post Content"
        )
        result = use_case.valid_data()
        assert result == expected_result


@patch.object(Post.objects, 'create_post', side_effect=create_post)  # we don't need to test django again
@patch.object(PostRegister, 'valid_data', return_value=None)  # already tested on TestValidData
class TestPostRegisterExecute(TestCase):
    # Test the execute method on PostRegister use case

    def setUp(self):
        # setup method will be executed on each test
        self._use_case = PostRegister(
            link="www.wordpress.com/posts/1",
            date="01/01/2021",
            title="Post",
            content="Post Content"
        )

    def test_return_post_type(self, mock_create, mock_register):
        result = self._use_case.execute()
        assert isinstance(result, Post)

    def test_create_post_with_link(self, mock_create, mock_register):
        expected_result = 'www.wordpress.com/posts/1'
        post = self._use_case.execute()
        assert post.link == expected_result

    def test_create_post_with_title(self, mock_create, mock_register):
        expected_result = 'Post'
        post = self._use_case.execute()
        assert post.title == expected_result
