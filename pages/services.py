from django.apps import apps
from .base_services import DownloadResponseHandler
from .classifier import Classifier


class PostDownloadResponseHandler(DownloadResponseHandler):

    def __init__(self):
        super().__init__()
        self._objects = self._get_fakenews_posts()  # get all posts (wordpress + soup)
        self._headers = ['date', 'link', 'title', 'content']
        self._filename = 'posts.csv'

    def _get_fakenews_posts(self):
        post_model = apps.get_app_config('fakenews').get_model('Post')
        return post_model.objects.get_all_posts()


class UserDownloadResponseHandler(DownloadResponseHandler):

    def __init__(self):
        super().__init__()
        self._objects = self._get_twitter_users()  # get Twitter users
        self._headers = ['name', 'username', 'created_at', 'description', 'location', 'profile_image_url', 'protected',
                         'public_metrics', 'url', 'verified', 'tweets']
        self._filename = 'users.csv'

    def _get_twitter_users(self):
        user_model = apps.get_app_config('twitter').get_model('User')
        return user_model.objects.get_all_users()


class TweetDownloadResponseHandler(DownloadResponseHandler):

    def __init__(self):
        super().__init__()
        self._objects = self.get_twitter_tweets()  # get Twitter tweets
        self._headers = ['text', 'author', 'conversation_id', 'created_at', 'lang', 'spreader', 'percentage']
        self._filename = 'tweets.csv'

    def get_twitter_tweets(self):
        tweet_model = apps.get_app_config('twitter').get_model('Tweet')
        return tweet_model.objects.get_all_tweets()

    def get_twitter_tweets_choices(self):
        tweet_model = apps.get_app_config('twitter').get_model('Tweet')
        return tweet_model.objects.get_all_tweets_choices()

    @property
    def objects(self):
        return self._objects


class ClassifierResponseHandler:

    def __init__(self, method, tweets):
        super().__init__()
        self._method = method
        self._tweets = tweets

    def handle_classifier(self):
        return Classifier(self._method, self._tweets).loading_classifier()
