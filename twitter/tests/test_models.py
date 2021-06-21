from django_mock_queries.query import MockSet
from django.test import TestCase
from mock import patch

from twitter.models import (
    Query,
    Tweet,
    User
)


class TestModelsManager(TestCase):
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

    @patch.object(User.objects, 'create', return_value=user_object[0])
    def _generate_user(self, mocked):
        return User.objects.create_user(
            _id=100,
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

    @patch.object(Tweet.objects, 'create', return_value=tweet_object[0])
    def _generate_tweet(self, mocked):
        return Tweet.objects.create_tweet(
            _id=100,
            text='texto de prueba',
            author=self.user_object,
            conversation_id=300,
            created_at='01/01/2021',
            lang='es'
        )

    @patch.object(Query.objects, 'create', return_value=query_object[0])
    def _generate_query(self, mocked):
        return Query.objects.create_query(
            text="query"
        )

    @patch.object(User.objects, 'get_queryset', return_value=qs_user_mock)
    def test_user_is_created_and_returned_by_id(self, mocked):
        result = list(User.objects.find_by_id(100))
        assert result == self.user_object

    def test_user_add_tweet_and_count_them(self):
        user = self._generate_user()
        tweets_before = len(user.tweets.all())

        tweet = self._generate_tweet()
        User.objects.add_tweet(user, tweet)
        tweets_now = len(user.tweets.all())

        assert tweets_now == tweets_before + 1

    @patch.object(User.objects, 'all', return_value=qs_user_mock)
    def test_user_get_all_and_return_1(self, mocked):
        users = User.objects.get_all_users()
        assert 1 == len(users)

    @patch.object(Tweet.objects, 'get_queryset', return_value=qs_tweet_mock)
    def test_tweet_is_created_and_returned_by_id(self, mocked):
        result = list(Tweet.objects.find_by_id(100))
        assert result == self.tweet_object

    @patch.object(Tweet.objects, 'all', return_value=qs_tweet_mock)
    def test_tweet_get_all_and_return_1(self, mocked):
        tweets = Tweet.objects.get_all_tweets()
        assert 1 == len(tweets)

    @patch.object(Query.objects, 'get_queryset', return_value=qs_query_mock)
    def test_query_is_created_and_returned_by_id(self, mocked):
        result = list(Query.objects.find_by_id(100))
        assert result == self.query_object

    @patch.object(Query.objects, 'get_queryset', return_value=qs_query_mock)
    def test_query_is_created_and_returned_by_text(self, mocked):
        result = list(Query.objects.find_by_text("query"))
        assert result == self.query_object

    @patch.object(Query.objects, 'find_by_id', return_value=qs_query_mock)
    def test_query_with_no_tweets_return_same_queryset(self, mocked):
        result = Query.objects.get_tweet_queryset(100)

        assert len(result) == len(self.query_object[0].tweets.all())

    def test_query_add_tweet_and_count_them(self):
        query = self._generate_query()
        tweets_before = len(query.tweets.all())

        tweet = self._generate_tweet()
        Query.objects.add_tweet(query, tweet)
        tweets_now = len(query.tweets.all())

        assert tweets_now == tweets_before + 1