from django.http import HttpResponse
from django_mock_queries.query import MockSet
from django.test import TestCase
from mock import patch
import pytest

from fakenews.base_models import FakeNews
from fakenews.base_register import PostRegister, PostAlreadyExistError
from fakenews.base_services import PostsResponseHandler, ResponseHandlerError
from fakenews.models import Wordpress, Post
from fakenews.services import WordpressResponseHandler


def generate_post():
    return Post(
        link="www.wordpress.com/posts/1",
        date="01/01/2021",
        title="Post",
        content="Post Content",
        fake_news_sources=dict
    )


def generate_posts():
    return [["01/01/2021",
             "www.wordpress.com/posts/1",
             "Post",
             "Post Content",
             None],
            ["01/01/2021",
             "www.wordpress.com/posts/2",
             "Post2",
             "Post2 Content",
             None]]


def generate_wordpress():
    return [
        Wordpress(
            id=100,
            url="www.wordpress.com/data",
            post_type="Pages",
            domain="www.wordpress.com"
        )
    ]


class TestFakeNewsResponseHandler(TestCase):

    @patch.object(Wordpress.objects, 'find_by_url', return_value=MockSet(generate_wordpress()[0]))
    @patch.object(Wordpress.objects, 'get_posts', return_value=generate_posts())
    def test_handle_download_response(self, find, get):
        handler = WordpressResponseHandler(
            url='www.wordpress.com/data'
        )
        result = handler.handle_download_response()

        assert isinstance(result, HttpResponse)
        assert (result['Content-Disposition']).endswith('.csv')

    @patch.object(Wordpress.objects, 'find_by_url', return_value=MockSet())
    @patch.object(Wordpress.objects, 'get_posts', return_value=generate_posts())
    def test_handle_download_response_empty_raises_ResponseHandlerError(self, find, get):
        with pytest.raises(ResponseHandlerError):
            handler = WordpressResponseHandler(
                url='www.wordpress.com/data'
            )
            result = handler.handle_download_response()


class TestPostsResponseHandler(TestCase):

    @patch.object(Post.objects, 'find_by_link', return_value=MockSet())
    @patch.object(PostRegister, 'execute', return_value=generate_post())
    @patch.object(FakeNews.objects, 'add_post', return_value=None)
    @patch('fakenews.base_services.PostRegister')
    def test_handle_post_response_creation_with_returned_data(self, register, find_by_link, execute, fakenews):
        post_handler = PostsResponseHandler()
        wordpress = generate_wordpress()[0]
        posts = generate_posts()
        post_handler.handle_post_response(wordpress, posts)

        register.assert_called_with(
            date="01/01/2021",
            link="www.wordpress.com/posts/2",
            title="Post2",
            content="Post2 Content",
            source_urls=None)

    @patch.object(Post.objects, 'find_by_link', return_value=MockSet())
    @patch.object(PostRegister, 'execute', side_effect=PostAlreadyExistError("error"))
    def test_handle_post_response_creation_raises_ResponseHandlerError(self, find_by_link, execute):
        with pytest.raises(ResponseHandlerError):
            post_handler = PostsResponseHandler()
            wordpress = generate_wordpress()[0]
            posts = generate_posts()
            post_handler.handle_post_response(wordpress, posts)
