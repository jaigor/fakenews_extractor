from django.utils.translation import gettext as _
from celery import shared_task
from celery_progress.backend import ProgressRecorder

from .scrapper import Scrapper, NoSoupTypeError, NoLinksFoundError
from .wordpress import WordpressAPI
from .base_services import (
    PostsResponseHandler,
    FakeNewsDoesNotExistError,
)
from .models import Wordpress, Soup

from .register import (
    WordpressRegister,
    SoupRegister
)
from .base_services import FakeNewsAlreadyExistError


# Custom Exceptions

class SoupDoesNotExistError(Exception):
    pass


class SoupAlreadyExistError(Exception):
    pass


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
            api = WordpressAPI(post_type_url)
            types = api.get_posts_types()

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
        progress_recorder = ProgressRecorder(self)
        progress_recorder.set_progress(0, len(post_type_url_list))

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

    except FakeNewsDoesNotExistError as err:
        raise FakeNewsDoesNotExistError(_(str(err)))
    except WordpressDoesNotExistError as err:
        raise WordpressDoesNotExistError(_(str(err)))


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

@shared_task(bind=True,
             throws=(
                     FakeNewsAlreadyExistError, SoupAlreadyExistError, FakeNewsDoesNotExistError,
                     SoupDoesNotExistError, NoSoupTypeError, NoLinksFoundError),
             trail=True, name="register_new_soup_posts")
def register_soup_posts(self, url, link_class, date_type, date_id, is_update):
    try:
        progress_recorder = ProgressRecorder(self)
        progress_recorder.set_progress(0, 100)

        # get all links
        api = Scrapper(url, link_class, date_type, date_id)
        links = api.get_collection()
        progress_recorder.set_progress(40, 100)
        # if no failure, register soup
        if is_update:
            # get soup
            soup = _get_soup(url)
        else:
            soup = _register_new_soup(url, link_class, date_type, date_id)

        progress_recorder.set_progress(50, 100)

        # register links
        posts = api.get_posts_content(links)
        progress_recorder.set_progress(80, 100)

        # register posts
        # delegate postresponsehandler
        post_handler = PostsResponseHandler()
        post_handler.handle_post_response(soup, posts)
        progress_recorder.set_progress(100, 100)

    except FakeNewsAlreadyExistError as err:
        raise FakeNewsAlreadyExistError(_(str(err)))
    except SoupAlreadyExistError as err:
        raise SoupAlreadyExistError(_(str(err)))
    except FakeNewsDoesNotExistError as err:
        raise FakeNewsDoesNotExistError(_(str(err)))
    except SoupDoesNotExistError as err:
        raise SoupDoesNotExistError(_(str(err)))
    except NoSoupTypeError as err:
        raise NoSoupTypeError(_(str(err)))
    except NoLinksFoundError as err:
        raise NoLinksFoundError(_(str(err)))


def _get_soup(url):
    fakenews_qs = Soup.objects.find_by_url(url)
    if not fakenews_qs.exists():
        # Raise a meaningful error to be cached by the client
        error_msg = (
            'No existe un Soup con esta url {} '
            'Por favor, pruebe otra consulta'
        ).format(url)

        raise SoupDoesNotExistError(_(error_msg))

    return fakenews_qs.get()


def _register_new_soup(url, link_class, date_type, date_id):
    register = SoupRegister(
        url=url,
        link_class=link_class,
        date_type=date_type,
        date_id=date_id,
    )
    return register.execute()
