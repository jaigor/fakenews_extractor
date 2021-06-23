from unittest.mock import patch

from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django_mock_queries.query import MockSet

from twitter.models import User, Tweet, Query
from twitter.views import QueryDetailView, QueryDeleteView


class TestTwitterView(TestCase):
    user_object = [
        User(
            id=100,
            name='name',
            username='username',
            created_at='01/01/2021',
            profile_image_url='profile_image_url',
            protected=True,
            public_metrics='public_metrics',
            verified=True,
            description='description',
            location='location',
            url='url'
        )
    ]
    qs_user_mock = MockSet(user_object[0])
    tweet_object = [
        Tweet(
            id=100,
            text='texto de prueba',
            author=user_object[0],
            conversation_id=300,
            created_at='01/01/2021',
            lang='es'
        )
    ]
    qs_tweet_mock = MockSet(tweet_object[0])
    query_object = [
        Query(
            id=100,
            text="query"
        )
    ]
    qs_query_mock = MockSet(query_object[0])

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.create_url = reverse('twitter:query-create')
        self.list_url = reverse('twitter:query-list')
        self.detail_url = reverse('twitter:query-detail', args=[100])
        self.delete_url = reverse('twitter:query-delete', args=[100])

    def test_query_create_view(self):
        response = self.client.get(self.create_url)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])
        self.assertTemplateUsed(response, 'twitters/query-create.html')

    def test_query_list_view(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'twitters/query-list.html')

    @patch.object(QueryDetailView, 'get_object', return_value=query_object[0])
    def test_query_GET_detail(self, mock_w):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'twitters/query-detail.html')

    @patch.object(QueryDeleteView, 'get_object', return_value=query_object[0])
    def test_query_delete_view(self, mock):
        response = self.client.get(self.delete_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'twitters/query-delete.html')

