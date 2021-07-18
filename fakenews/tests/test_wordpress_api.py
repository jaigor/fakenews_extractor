from django.test import TestCase
import pytest
import os
from django.http import HttpResponse

from fakenews.wordpress import (
    WordpressAPI,
    NoOKResponseError,
    TooManyRequestError
)


class TestWordpressAPI(TestCase):

    def test_get_posts_types_missing_protocol_url_raises_NoOKResponseError(self):
        with pytest.raises(NoOKResponseError):
            wordpress = WordpressAPI(
                "www.wrongurl.com"
            )
            wordpress.get_posts_types()

    def test_get_posts_types_incorrect_url_raises_NoOKResponseError(self):
        with pytest.raises(NoOKResponseError):
            wordpress = WordpressAPI(
                "http://www.wrongurl.com"
            )
            wordpress.get_posts_types()

    def test_get_posts_types_no_wordpress_access_url_raises_TooManyRequestError(self):
        with pytest.raises(TooManyRequestError):
            wordpress = WordpressAPI(
                "http://www.maldita.es/malditobulo/"
            )
            wordpress.get_posts_types()

    def test_get_posts_types_and_return_some_type(self):
        correct_wordpress = WordpressAPI(
            "https://www.snopes.com/"  # this can change with time
        )
        types = correct_wordpress.get_posts_types()
        assert len(types.keys()) > 0

    def test_get_posts_content_and_return_posts(self):
        correct_post = WordpressAPI(
            "https://www.snopes.com/"  # this can change with time
        )
        posts = correct_post.get_posts_content("https://www.snopes.com/wp-json/wp/v2/posts/", None)
        assert len(posts) > 0

    def test_get_csv_response_and_check_file_is_deleted(self):
        correct_post = WordpressAPI(
            "https://www.snopes.com/"  # this can change with time
        )
        filename = "data.csv"
        posts = correct_post.get_posts_content("https://www.snopes.com/wp-json/wp/v2/posts/", None)
        response = correct_post.get_csv_response(filename, posts, ['date', 'link', 'title', 'content'])

        assert not os.path.isfile(filename)

    def test_get_csv_response_and_check_file_is_httpresponse(self):
        correct_post = WordpressAPI(
            "https://www.snopes.com/"  # this can change with time
        )
        filename = "data.csv"
        posts = correct_post.get_posts_content("https://www.snopes.com/wp-json/wp/v2/posts/", None)
        response = correct_post.get_csv_response(filename, posts, ['date', 'link', 'title', 'content'])

        assert isinstance(response, HttpResponse)
