from celery import chain
from django.utils.translation import gettext as _
from urllib.parse import urlparse

from .wordpress import WordpressAPI
from .scrapper import Scrapper

from .models import Wordpress, Soup
from .base_services import (
    FakeNewsResponseHandler,
    FakeNewsAlreadyExistError,
    FakeNewsDoesNotExistError
)

from .tasks import (
    get_wordpress_urls,
    register_wordpress_list_posts,
    register_soup_posts
)
from .register import (
    WordpressDoesNotExistError,
    WordpressAlreadyExistError,
    SoupDoesNotExistError,
    SoupAlreadyExistError
)


# Custom Exceptions
class PostAlreadyExistError(Exception):
    pass


class PostDoesNotExistError(Exception):
    pass


def propagate_chain_get(terminal_node, timeout=None):
    node = terminal_node.parent
    while node:
        node.get(propagate=True, timeout=timeout)
        node = node.parent


# Wordpress #
class WordpressResponseHandler(FakeNewsResponseHandler):

    def get_queryset(self, id):
        try:
            return Wordpress.objects.get_post_queryset(id)
        except WordpressDoesNotExistError as err:
            raise FakeNewsDoesNotExistError(_(str(err)))

    def _handle(self):
        result = None
        try:
            result = chain(get_wordpress_urls.s(self._url, False),
                           register_wordpress_list_posts.s()).apply_async()
            propagate_chain_get(result)
            return result
        except WordpressAlreadyExistError as err:
            result.revoke()
            raise FakeNewsAlreadyExistError(_(str(err)))
        except FakeNewsAlreadyExistError as err:
            result.revoke()
            raise FakeNewsAlreadyExistError(_(str(err)))

    def _update(self):
        result = None
        try:
            result = chain(get_wordpress_urls.s(self._url, True),
                           register_wordpress_list_posts.s()).apply_async()
            propagate_chain_get(result)
            return result
        except WordpressDoesNotExistError as err:
            result.revoke()
            raise FakeNewsDoesNotExistError(_(str(err)))
        except FakeNewsDoesNotExistError as err:
            result.revoke()
            raise FakeNewsDoesNotExistError(_(str(err)))

    def _download(self):
        try:
            posts = self._get_internal_posts()
            w = self._get_fakenews()
            filename = w.post_type + '.csv'
            return WordpressAPI(self._url).get_csv_response(filename, posts)
        except WordpressDoesNotExistError as err:
            raise FakeNewsDoesNotExistError(_(str(err)))

    def _get_fakenews(self):
        fakenews_qs = Wordpress.objects.find_by_url(self._url)
        if not fakenews_qs.exists():
            # Raise a meaningful error to be cached by the client
            error_msg = (
                'No existe un Wordpress con esta url {} '
                'Por favor, pruebe otra consulta'
            ).format(self._url)

            raise WordpressDoesNotExistError(_(error_msg))

        return fakenews_qs.get()

    def _get_internal_posts(self):
        # valid data
        w = self._get_fakenews()
        return Wordpress.objects.get_posts(w.id)


# Soup #
class SoupResponseHandler(FakeNewsResponseHandler):

    def __init__(self, url=None, link_class=None, date_type=None, date_id=None):
        super().__init__(url)
        self._url = url
        self._link_class = link_class
        self._date_type = date_type
        self._date_id = date_id

    def get_queryset(self, id):
        try:
            return Soup.objects.get_post_queryset(id)
        except SoupDoesNotExistError as err:
            raise FakeNewsDoesNotExistError(_(str(err)))

    def _handle(self):
        result = None
        try:
            result = register_soup_posts.s(self._url, self._link_class, self._date_type, False).apply_async()
            return result
        except SoupAlreadyExistError as err:
            result.revoke()
            raise FakeNewsAlreadyExistError(_(str(err)))
        except FakeNewsAlreadyExistError as err:
            result.revoke()
            raise FakeNewsAlreadyExistError(_(str(err)))

    def _update(self):
        result = None
        try:
            result = register_soup_posts.s(self._url, self._link_class, self._date_type, True).apply_async()
            return result
        except SoupDoesNotExistError as err:
            result.revoke()
            raise FakeNewsDoesNotExistError(_(str(err)))
        except FakeNewsDoesNotExistError as err:
            result.revoke()
            raise FakeNewsDoesNotExistError(_(str(err)))

    def _download(self):
        try:
            posts = self._get_internal_posts()
            filename = urlparse(self._url).netloc + '.csv'

            return Scrapper(self._url).get_csv_response(filename, posts)
        except SoupDoesNotExistError as err:
            raise FakeNewsDoesNotExistError(_(str(err)))

    def _get_internal_posts(self):
        # valid data
        s = self._get_fakenews()
        return Soup.objects.get_posts(s.id)

    def _get_fakenews(self):
        fakenews_qs = Soup.objects.find_by_url(self._url)
        if not fakenews_qs.exists():
            # Raise a meaningful error to be cached by the client
            error_msg = (
                'No existe un Soup con esta url {} '
                'Por favor, pruebe otra consulta'
            ).format(self._url)

            raise SoupDoesNotExistError(_(error_msg))

        return fakenews_qs.get()
