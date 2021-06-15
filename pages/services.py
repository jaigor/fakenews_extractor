from django.utils.translation import gettext as _

from django.apps import apps
from .downloader import (
    Downloader
)


# Custom Exceptions
class ResponseHandlerError(Exception):
    pass


class DownloadResponseHandler:

    def __init__(self):
        pass

    def handle_all_posts_response(self):
        try:
            # get all posts (wordpress + soup)
            posts = self._get_fakenews_posts()

            headers = ['date', 'link', 'title', 'content']
            # generate csv response
            filename = 'posts.csv'
            return Downloader().get_csv_response(filename, posts, headers)
        except (
                Exception
        ) as err:
            raise ResponseHandlerError(_(str(err)))

    def handle_all_users_response(self):
        try:
            # get Twiiter users
            users = self._get_twitter_users()

            headers = ['name', 'username', 'created_at', 'description', 'location', 'profile_image_url', 'protected',
                       'public_metrics', 'url', 'verified']
            # generate csv response            
            filename = 'users.csv'
            return Downloader().get_csv_response(filename, users, headers)
        except (
                Exception
        ) as err:
            raise ResponseHandlerError(_(str(err)))

    def _get_fakenews_posts(self):
        post_model = apps.get_app_config('fakenews').get_model('Post')
        return post_model.objects.get_all_posts()

    def _get_twitter_users(self):
        user_model = apps.get_app_config('twitter').get_model('User')
        return user_model.objects.get_all_users()
