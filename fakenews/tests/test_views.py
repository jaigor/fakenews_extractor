from unittest.mock import patch

from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django_mock_queries.query import MockSet

from fakenews.models import Wordpress, Post
from fakenews.views import WordpressDetailView, WordpressDeleteView


class TestIndexView(TestCase):

    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        response = self.client.get('/fakenews/')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')


class TestWordpressView(TestCase):
    wordpress_object = [
        Wordpress(
            id=100,
            url="www.wordpress.com/data",
            post_type="Pages",
            domain="www.wordpress.com"
        )
    ]
    qs_wordpress_mock = MockSet(wordpress_object[0])
    post_object = [
        Post(
            link="www.wordpress.com/posts/1",
            date="01/01/2021",
            title="Post",
            content="Post Content"
        )
    ]
    qs_post_mock = MockSet(post_object[0])

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.create_url = reverse('fakenews:wordpress-create')
        self.list_url = reverse('fakenews:wordpress-list')
        self.detail_url = reverse('fakenews:wordpress-detail', args=[100])
        self.delete_url = reverse('fakenews:wordpress-delete', args=[100])

    def test_wordpress_create_view(self):
        response = self.client.get(self.create_url)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])
        self.assertTemplateUsed(response, 'wordpress/wordpress-create.html')

    def test_wordpress_list_view(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wordpress/wordpress-list.html')

    @patch.object(WordpressDetailView, 'get_object', return_value=wordpress_object[0])
    @patch.object(Wordpress, 'get_posts_url', return_value="www.wordpress.com/data")
    def test_wordpress_GET_detail(self, mock_w, mock_p):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wordpress/wordpress-detail.html')

    @patch.object(WordpressDeleteView, 'get_object', return_value=wordpress_object[0])
    def test_wordpress_delete_view(self, mock):
        response = self.client.get(self.delete_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wordpress/wordpress-delete.html')
