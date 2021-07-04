from celery_progress.backend import ProgressRecorder
from django_mock_queries.query import MockSet
from django.test import TestCase
from mock import patch

from twitter.models import User, Tweet, Query
from twitter.register import UserRegister, TweetRegister
from twitter.tasks import get_tweets_response, register_tweets
from twitter.twitter import TweetLookup, UserLookup


class TestWordpressTasks(TestCase):
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
    expected_tweets = {
        'created_at': '2021-06-23T10:10:48.000Z', 'id': '1407642286956056579',
        'conversation_id': '1407642286956056579',
        'text': "RT @DaysForGirls: How does #menstrualequity relate to #selfcare? Join DfG, @washunited &amp; "
                "@MietAfrica next week as we kick off this year's S…",
        'lang': 'en', 'author_id': '1398144816223948803'
    }

    expected_user = {
        'id': 100,
        'name': 'name',
        'username': 'username',
        'created_at': '01/01/2021',
        'profile_image_url': 'profile_image_url',
        'protected': True,
        'public_metrics': 'public_metrics',
        'verified': True,
        'description': 'description',
        'location': 'location',
        'url': 'url'
    }

    @patch.object(TweetLookup, 'search_tweets', return_value=expected_tweets)
    @patch.object(ProgressRecorder, 'set_progress')
    def test_get_tweets_response(self, get_post_types, progress):
        tweets = get_tweets_response('texto')

        assert tweets == self.expected_tweets

    @patch.object(Tweet.objects, 'find_by_id', return_value=MockSet())
    @patch.object(User.objects, 'find_by_id', return_value=MockSet())
    @patch.object(UserLookup, 'search_user', return_value=expected_user)
    @patch.object(UserRegister, 'execute', return_value=user_object[0])
    @patch.object(TweetRegister, 'execute', return_value=tweet_object[0])
    @patch.object(Tweet.objects, 'find_by_id', return_value=qs_tweet_mock)
    @patch.object(MockSet, 'get')
    @patch.object(User.objects, 'add_tweet')
    @patch.object(Query.objects, 'find_by_text', return_value=qs_query_mock)
    @patch.object(Query.objects, 'add_tweet')
    @patch.object(ProgressRecorder, 'set_progress')
    def test_register_tweets_with_new_user(self, progress, ufind, usearch, uexecute, texecute, tfinf2, tget,
                                           uadd, qfind, qadd, tfind):
        register_tweets([self.expected_tweets], 'texto')

        assert ufind.called
        assert usearch.called
        assert uexecute.called
        assert texecute.called
