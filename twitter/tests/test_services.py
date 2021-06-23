from django.http import HttpResponse
from django_mock_queries.query import MockSet
from django.test import TestCase
from mock import patch
import pytest

from twitter.models import Query, User
from twitter.services import ResponseHandler, ResponseHandlerError

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


def generate_tweets():
    return [[100,
             'texto de prueba',
             user_object[0],
             300,
             '01/01/2021',
             'es']
            ]


query_object = [
    Query(
        id=100,
        text="query"
    )
]
qs_query_mock = MockSet(query_object[0])


class TestResponseHandler(TestCase):

    @patch.object(Query.objects, 'find_by_text', return_value=qs_query_mock)
    @patch.object(Query.objects, 'get_tweets', return_value=generate_tweets())
    def test_handle_download_response(self, find, get):
        handler = ResponseHandler(
            query='query'
        )
        result = handler.handle_download_response()

        assert isinstance(result, HttpResponse)
        assert (result['Content-Disposition']).endswith('.csv')

    @patch.object(Query.objects, 'find_by_text', return_value=MockSet())
    @patch.object(Query.objects, 'get_tweets', return_value=generate_tweets())
    def test_handle_download_response_empty_raises_ResponseHandlerError(self, find, get):
        with pytest.raises(ResponseHandlerError):
            handler = ResponseHandler(
                query='query'
            )
            result = handler.handle_download_response()
