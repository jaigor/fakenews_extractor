from django.test import TestCase
import pytest

from twitter.twitter import TweetLookup, TweetsRequestError, UserLookup, UserRequestError


class TestTwitterAPI(TestCase):

    def test_get_tweets_with_wrong_text_raises_TweetsRequestError(self):
        with pytest.raises(TweetsRequestError):
            twitter = TweetLookup(
                "2121212127893457394857678594769"
            )
            tweets = twitter.search_tweets()

    def test_get_tweets_with_normal_text_returns_something(self):
        twitter = TweetLookup(
            "texto"
        )
        tweets = twitter.search_tweets()

        assert len(tweets) > 0

    def test_get_user_with_wrong_id_raises_UserRequestError(self):
        with pytest.raises(UserRequestError):
            twitter = UserLookup(
                '123'
            )
            user = twitter.search_user()

    def test_get_user_with_normal_id_returns_something(self):
        twitter = UserLookup(
            6253282
        )
        user = twitter.search_user()

        assert len(user) > 0