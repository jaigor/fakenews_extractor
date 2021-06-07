from django.utils.translation import gettext as _
from celery import shared_task
from celery_progress.backend import ProgressRecorder

from .scrapper import Scrapper
from .wordpress import WordpressAPI
from .base_services import (
    PostsResponseHandler,
    FakeNewsDoesNotExistError,
)
from .models import Wordpress, Soup

from .register import (
    WordpressRegister,
    WordpressDoesNotExistError,
    WordpressAlreadyExistError,
    SoupRegister,
    SoupDoesNotExistError,
    SoupAlreadyExistError
)
from .base_services import FakeNewsAlreadyExistError


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

@shared_task(bind=True,
             throws=(FakeNewsAlreadyExistError, SoupAlreadyExistError, FakeNewsDoesNotExistError, SoupDoesNotExistError),
             trail=True, name="register_new_soup_posts")
def register_soup_posts(self, url, link_class, date_type, date_id, is_update):
    try:
        progress_recorder = ProgressRecorder(self)
        progress_recorder.set_progress(0, 100)

        # get all links
        links = _get_external_links(url, link_class, date_type, date_id)
        progress_recorder.set_progress(40, 100)
        # if no failure, register soup
        if is_update:
            # get soup
            soup = _get_soup(url)
        else:
            soup = _register_new_soup(url, link_class, date_type, date_id)

        progress_recorder.set_progress(50, 100)

        # register links
        posts = _get_external_posts(url, link_class, date_type, date_id, links)
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


def _get_external_links(url, link_class, date_type, date_id):
    scrapper = Scrapper(url,
                        link_class,
                        date_type,
                        date_id)
    return scrapper.get_collection()


def _get_external_posts(url, link_class, date_type, date_id, links):
    scrapper = Scrapper(url,
                        link_class,
                        date_type,
                        date_id)

    return scrapper.get_posts_content(links)


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
    soup = SoupRegister(
        url=url,
        link_class=link_class,
        date_type=date_type,
        date_id=date_id,
    )
    return soup.execute()

