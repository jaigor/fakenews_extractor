from django.utils.translation import gettext as _
from celery import shared_task
from celery_progress.backend import ProgressRecorder


from .wordpress import WordpressAPI
from .base_services import (
    PostsResponseHandler,
    FakeNewsDoesNotExistError,
)
from .models import Wordpress, Soup

from .register import WordpressRegister
from .base_services import FakeNewsAlreadyExistError


class WordpressDoesNotExistError(Exception):
    pass


class WordpressAlreadyExistError(Exception):
    pass


@shared_task(bind=True, throws=(FakeNewsAlreadyExistError, WordpressAlreadyExistError),
             trail=True, name="get_wordpress_urls")
def get_wordpress_urls(self, post_type_url, is_update):
    try:
        urls = []
        if is_update:
            # update in task posts
            urls.append(post_type_url)

        else:
            # get types of posts
            types = _get_types(post_type_url)
            count = 0
            progress_recorder = ProgressRecorder(self)
            progress_recorder.set_progress(count, len(types.items()))

            # if no failure, register wordpress
            for k, v in types.items():
                # register each wordpress
                _register_new_wordpress(v, k)
                urls.append(v)
                progress_recorder.set_progress(count + 1, len(types.items()))
        return urls

    except FakeNewsAlreadyExistError as err:
        raise FakeNewsAlreadyExistError(_(str(err)))
    except WordpressAlreadyExistError as err:
        raise WordpressAlreadyExistError(_(str(err)))


@shared_task(bind=True, throws=(FakeNewsDoesNotExistError, WordpressDoesNotExistError),
             trail=True, name="register_wordpress_list_posts")
def register_wordpress_list_posts(self, post_type_url_list):
    try:
        if len(post_type_url_list) < 1:
            return

        progress_recorder = ProgressRecorder(self)
        progress_recorder.set_progress(0, len(post_type_url_list))

        count = 0
        for url in post_type_url_list:
            print(url)
            api = WordpressAPI(url)
            posts = api.get_posts_content(url)
            progress_recorder.set_progress(count + 0.5, len(post_type_url_list))

            # register posts
            # delegate on postresponsehandler
            post_handler = PostsResponseHandler()
            wordpress = _get_wordpress(url)
            post_handler.handle_post_response(wordpress, posts)
            progress_recorder.set_progress(count + 0.5, len(post_type_url_list))

    except FakeNewsDoesNotExistError as err:
        raise FakeNewsDoesNotExistError(_(str(err)))
    except WordpressDoesNotExistError as err:
        raise WordpressDoesNotExistError(_(str(err)))


def _get_types(url):
    wordpress = WordpressAPI(url)
    return wordpress.get_posts_types()


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


def _register_new_wordpress(url, post_type):
    register = WordpressRegister(
        url=url,
        post_type=post_type
    )
    return register.execute()


# Soup #

@shared_task(bind=True, trail=True, name="register_new_soup_posts")
def c_register_soup_posts(self, post_type_url):
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
