from celery import shared_task
from celery_progress.backend import ProgressRecorder
from django.utils.translation import gettext as _

from twitter.models import Tweet, User, Query
from twitter.register import UserRegister, TweetRegister, TweetAlreadyExistError, UserAlreadyExistError
from twitter.twitter import TweetLookup, TweetsRequestError, UserLookup, UserRequestError


class TaskHandlerError(Exception):
    pass


@shared_task(bind=True, throws=(TweetsRequestError, TaskHandlerError),
             trail=True, name="get_tweets_urls")
def get_tweets_response(self, query):

    try:
        progress_recorder = ProgressRecorder(self)
        progress_recorder.set_progress(0, 100)

        twitter = TweetLookup(query)
        tweets = twitter.search_tweets()
        progress_recorder.set_progress(100, 100)

        return tweets
    except (
            TweetsRequestError
    ) as err:
        raise TaskHandlerError(_(str(err)))


@shared_task(bind=True, throws=(TweetAlreadyExistError, UserAlreadyExistError, UserRequestError, TaskHandlerError),
             trail=True, name="register_tweets")
def register_tweets(self, tweets, query):

    try:
        count = 0
        progress_recorder = ProgressRecorder(self)
        progress_recorder.set_progress(count, len(tweets))

        for t in tweets:
            # get or create tweet
            tweet_id = t['id']
            tweet_qs = Tweet.objects.find_by_id(tweet_id)
            if tweet_qs.exists():
                print("Ya existe un tweet con ese id")
            else:
                # get or create user
                author_id = t['author_id']
                user = User.objects.find_by_id(author_id)
                if not user.exists():
                    register = UserResponseHandler(author_id)
                    register.register_new_user()

                # create tweet
                _register_new_tweet(t)

                # link user to tweet
                user = User.objects.find_by_id(author_id)
                Tweet.objects.add_author(tweet_id, user)

                # link tweet to the users list
                tweet_qs = Tweet.objects.find_by_id(tweet_id)
                User.objects.add_tweet(author_id, tweet_qs.get())

            # add existent or new tweet to query
            Query.objects.add_tweet(query, tweet_qs.get())

            progress_recorder.set_progress(count + 1, len(tweets))
    except (
            TweetAlreadyExistError,
            UserAlreadyExistError,
            UserRequestError
    ) as err:
        raise TaskHandlerError(_(str(err)))


def _register_new_tweet(t):
    # create tweet
    tweet = TweetRegister(
        _id=t['id'],
        text=t['text'],
        conversation_id=t['conversation_id'],
        created_at=t['created_at'],
        lang=t['lang'],
        author_id=None
    )
    tweet.execute()


class UserResponseHandler:

    def __init__(
            self,
            author_id
    ):
        self._author_id = author_id

    def register_new_user(self):
        user_response = self._get_user_response()
        # create new one
        # fields that can not be returned
        description = self._fill_field(user_response, 'description')
        location = self._fill_field(user_response, 'location')
        url = self._fill_field(user_response, 'url')

        user = UserRegister(
            _id=user_response['id'],
            name=user_response['name'],
            username=user_response['username'],
            created_at=user_response['created_at'],
            profile_image_url=user_response['profile_image_url'],
            protected=user_response['protected'],
            public_metrics=user_response['public_metrics'],
            verified=user_response['verified'],
            description=description,
            location=location,
            url=url,
            tweet_id=None
        )
        user.execute()

    def _get_user_response(self):
        twitter = UserLookup(self._author_id)
        return twitter.search_user()

    def _fill_field(self, dictionary, attr):
        try:
            return dictionary[attr]
        except KeyError:
            return None
