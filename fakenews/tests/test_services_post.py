from django_mock_queries.query import MockSet
from django.test import TestCase
from mock import patch
import pytest

from fakenews.base_services import PostsResponseHandler
from fakenews.models import Wordpress
from fakenews.services import (
    WordpressDoesNotExistError
)


class TestPostsResponseHandler(TestCase):
    posts = [["www.wordpress.com/posts/1",
              "01/01/2021",
              "Post",
              "Post Content"],
             ["www.wordpress.com/posts/2",
              "01/01/2021",
              "Post2",
              "Post2 Content"]]

    @patch.object(Wordpress.objects, 'find_by_id', return_value=MockSet())
    def test_when_wordpress_does_not_exist_raise_does_not_exist_error(self, mocked):
        with pytest.raises(WordpressDoesNotExistError):
            use_case = PostsResponseHandler(
                url="www.wordpress.com/data"
            )
            use_case._get_fakenews()
