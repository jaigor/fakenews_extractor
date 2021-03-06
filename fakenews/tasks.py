from django.utils.translation import gettext as _
from celery import shared_task
from celery_progress.backend import ProgressRecorder

from .scrapper import Scrapper, NoSoupTypeError, NoLinksFoundError
from .url_extractor import UrlPattern, UrlClass
from .wordpress import WordpressAPI, TooManyRequestError, NoOKResponseError
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


class FakeNewsError(Exception):
    pass


@shared_task(bind=True, throws=(FakeNewsAlreadyExistError, WordpressAlreadyExistError,
                                TooManyRequestError, NoOKResponseError, FakeNewsError),
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
    except (TooManyRequestError, NoOKResponseError) as err:
        raise FakeNewsError(_(str(err)))


@shared_task(bind=True, throws=(FakeNewsDoesNotExistError, WordpressDoesNotExistError,
                                TooManyRequestError, NoOKResponseError),
             trail=True, name="register_wordpress_list_posts")
def register_wordpress_list_posts(self, post_type_url_list,
                                  f_source_pattern=None, f_source_type=None, f_source_entire_link=None,
                                  s_source_pattern=None, s_source_type=None, s_source_entire_link=None):
    try:
        progress_recorder = ProgressRecorder(self)
        progress_recorder.set_progress(0, len(post_type_url_list))

        count = 0
        for url in post_type_url_list:
            api = WordpressAPI(url)

            url_nodes = register_fake_news_source(f_source_pattern, f_source_type, f_source_entire_link,
                                                  s_source_pattern, s_source_type, s_source_entire_link)
            # send url_nodes, foreach post search --> modify urlextractor
            posts = api.get_posts_content(url, url_nodes)
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
def register_soup_posts(self, is_update, url, link_class, date_type, date_id, body_class=None,
                        f_source_pattern=None, f_source_type=None, f_source_entire_link=None,
                        s_source_pattern=None, s_source_type=None, s_source_entire_link=None):
    try:
        progress_recorder = ProgressRecorder(self)
        progress_recorder.set_progress(0, 100)

        if body_class is not None:
            print("body " + body_class)

        # get all links
        api = Scrapper(url, link_class, date_type, date_id, body_class)
        links = api.get_collection()
        progress_recorder.set_progress(40, 100)

        # if no failure, register soup
        if is_update:
            # get soup
            soup = _get_soup(url)
        else:
            soup = _register_new_soup(url, link_class, date_type, date_id, body_class)

        progress_recorder.set_progress(50, 100)

        url_nodes = register_fake_news_source(f_source_pattern, f_source_type, f_source_entire_link,
                                              s_source_pattern, s_source_type, s_source_entire_link)

        # register links
        posts = api.get_posts_content(links, url_nodes)
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


def _register_new_soup(url, link_class, date_type, date_id, body_class=None):
    register = SoupRegister(
        url=url,
        link_class=link_class,
        date_type=date_type,
        date_id=date_id,
        body_class=body_class
    )
    return register.execute()


# Fake News Url
def get_fake_news_source():
    pass


def register_fake_news_source(f_source_pattern=None, f_source_type=None, f_source_entire_link=None,
                              s_source_pattern=None, s_source_type=None, s_source_entire_link=None):
    # register fake news url/s
    url_nodes = []
    if f_source_pattern is not None and f_source_pattern != "":
        url_nodes.append(_create_node(f_source_type, f_source_pattern, f_source_entire_link))

    if s_source_pattern is not None and s_source_pattern != "":
        url_nodes.append(_create_node(s_source_type, s_source_pattern, s_source_entire_link))

    return url_nodes


def _create_node(source_type, source_pattern, source_entire_link):
    if source_type == "1":
        return UrlPattern(source_pattern, source_entire_link)
    else:
        return UrlClass(source_pattern)
