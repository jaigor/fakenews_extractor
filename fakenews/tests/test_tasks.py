from celery_progress.backend import ProgressRecorder
from django_mock_queries.query import MockSet
from django.test import TestCase
from mock import patch
import pytest

from fakenews.base_register import FakeNewsAlreadyExistError, FakeNewsDoesNotExistError
from fakenews.models import Wordpress, Soup
from fakenews.register import WordpressRegister
from fakenews.scrapper import Scrapper
from fakenews.tasks import get_wordpress_urls, register_wordpress_list_posts, register_soup_posts
from fakenews.wordpress import WordpressAPI


wordpress_object = [
    Wordpress(
        id=100,
        url="www.wordpress.com/data",
        post_type="Pages",
        domain="www.wordpress.com"
    )
]
qs_wordpress_mock = MockSet(wordpress_object[0])
soup_object = [
    Soup(
        id=100,
        url="www.wordpress.com/data",
        link_class="article",
        date_type="1",
        date_id="date"
    )
]
qs_soup_mock = MockSet(soup_object[0])

posts_types = {'Pages': 'www.wordpress.com/data'}
posts_content = [['date', 'link', 'title', 'content']]
links = ['www.wordpress.com/data']


class TestWordpressTasks(TestCase):

    def test_urls_get_with_update(self):
        post_type_url = 'http://www.wordpress.com/wp-json'
        urls = get_wordpress_urls(post_type_url, True)

        assert urls == [post_type_url]

    @patch.object(WordpressAPI, 'get_posts_types', return_value=posts_types)
    @patch.object(WordpressRegister, 'execute', return_value=wordpress_object[0])
    @patch.object(ProgressRecorder, 'set_progress')
    def test_urls_get_with_create(self, get_post_types, register, progress):
        expected_type_url = 'www.wordpress.com/data'
        urls = get_wordpress_urls('http://www.wordpress.com/', False)

        assert urls == [expected_type_url]

    @patch.object(WordpressAPI, 'get_posts_types', return_value=posts_types)
    @patch.object(WordpressRegister, 'execute', side_effect=FakeNewsAlreadyExistError("error"))
    @patch.object(ProgressRecorder, 'set_progress')
    def test_urls_get_with_create_raises_FakeNewsAlreadyExistError(self, get_post_types, execute, progress):
        with pytest.raises(FakeNewsAlreadyExistError):
            urls = get_wordpress_urls('http://www.wordpress.com/', False)

    @patch.object(WordpressAPI, 'get_posts_content', return_value=posts_content)
    @patch.object(Wordpress.objects, 'find_by_url', return_value=qs_wordpress_mock)
    @patch.object(ProgressRecorder, 'set_progress')
    @patch('fakenews.tasks.PostsResponseHandler.handle_post_response')
    def test_post_lists_get_with_create(self, postresponse, get_post_types, find_by_url, progress):
        register_wordpress_list_posts(links)

        postresponse.assert_called_with(qs_wordpress_mock.get(), posts_content)

    @patch.object(WordpressAPI, 'get_posts_content', return_value=posts_content)
    @patch.object(Wordpress.objects, 'find_by_url', side_effect=FakeNewsAlreadyExistError("error"))
    @patch.object(ProgressRecorder, 'set_progress')
    def test_post_lists_get_with_create_raises_FakeNewsAlreadyExistError(self, get_post_types, execute, progress):
        with pytest.raises(FakeNewsAlreadyExistError):
            register_wordpress_list_posts(links)


class TestSoupTasks(TestCase):

    @patch.object(ProgressRecorder, 'set_progress')
    @patch.object(Scrapper, 'get_collection', return_value=links)
    @patch.object(Soup.objects, 'find_by_url', return_value=qs_soup_mock)
    @patch.object(Scrapper, 'get_posts_content', return_value=posts_content)
    @patch('fakenews.tasks.PostsResponseHandler.handle_post_response')
    def test_register_soup_get_with_update(self, postresponse, progress, scrapper, find_url, get_post_content):
        register_soup_posts(
            url="www.wordpress.com/data",
            link_class="article",
            date_type="1",
            date_id="date",
            is_update=True)

        postresponse.assert_called_with(qs_soup_mock.get(), posts_content)

    @patch.object(ProgressRecorder, 'set_progress')
    @patch.object(Scrapper, 'get_collection', return_value=links)
    @patch.object(Soup.objects, 'find_by_url', side_effect=FakeNewsAlreadyExistError("error"))
    def test_register_soup_raises_FakeNewsAlreadyExistError(self, progress, scrapper, find_url):
        with pytest.raises(FakeNewsAlreadyExistError):
            register_soup_posts(
                url="www.wordpress.com/data",
                link_class="article",
                date_type="1",
                date_id="date",
                is_update=False)

    @patch.object(ProgressRecorder, 'set_progress')
    @patch.object(Scrapper, 'get_collection', return_value=links)
    @patch.object(Soup.objects, 'find_by_url', side_effect=FakeNewsDoesNotExistError("error"))
    def test_register_soup_raises_FakeNewsDoesNotExistError(self, progress, scrapper, find_url):
        with pytest.raises(FakeNewsDoesNotExistError):
            register_soup_posts(
                url="www.wordpress.com/data",
                link_class="article",
                date_type="1",
                date_id="date",
                is_update=True)