from django.utils.translation import gettext as _
from celery import shared_task
from celery_progress.backend import ProgressRecorder
from .wordpress import WordpressAPI
from .base_services import (
    PostsResponseHandler,
)
from .models import Wordpress, Soup


class WordpressDoesNotExistError(Exception):
    pass


@shared_task(bind=True, trail=True, name="register_new_wordpress_posts")
def c_register_wordpress_posts(self, post_type_url):
    progress_recorder = ProgressRecorder(self)
    progress_recorder.set_progress(10, 100)

    api = WordpressAPI(post_type_url)
    posts = api.get_posts_content(post_type_url)
    progress_recorder.set_progress(60, 100)

    # register posts
    # delegate on postresponsehandler
    post_handler = PostsResponseHandler()
    progress_recorder.set_progress(70, 100)

    wordpress = _get_wordpress(post_type_url)
    post_handler.handle_post_response(wordpress, posts)


@shared_task(bind=True, trail=True, name="update_wordpress_posts")
def c_register_wordpress_list_posts(self, post_type_url_list):
    progress_recorder = ProgressRecorder(self)

    count = 0
    for url in post_type_url_list:
        api = WordpressAPI(url)
        posts = api.get_posts_content(url)
        progress_recorder.set_progress(count + 0.5, len(post_type_url_list))

        # register posts
        # delegate on postresponsehandler
        post_handler = PostsResponseHandler()
        wordpress = _get_wordpress(url)
        post_handler.handle_post_response(wordpress, posts)
        progress_recorder.set_progress(count + 0.5, len(post_type_url_list))


def _get_wordpress(url):
    fakenews_qs = Wordpress.objects.find_by_url(url)
    if not fakenews_qs.exists():
        # Raise a meaningful error to be cached by the client
        error_msg = (
            'No existe un Wordpress con esta url {} '
            'Por favor, pruebe otra consulta'
        ).format(url)

        raise WordpressDoesNotExistError(_(error_msg))

    return fakenews_qs.get()
