from celery import chain
from django.utils.translation import gettext as _
from urllib.parse import urlparse

from .models import Wordpress, Soup
from .base_services import (
    FakeNewsResponseHandler,
    FakeNewsAlreadyExistError,
    FakeNewsDoesNotExistError
)

from .tasks import (
    get_wordpress_urls,
    register_wordpress_list_posts,
    register_soup_posts,

    WordpressDoesNotExistError,
    WordpressAlreadyExistError,
    SoupDoesNotExistError,
    SoupAlreadyExistError
)


# chain propagator
def propagate_chain_get(terminal_node, timeout=None):
    node = terminal_node.parent
    while node:
        node.get(propagate=True, timeout=timeout)
        node = node.parent


# Wordpress #
class WordpressResponseHandler(FakeNewsResponseHandler):

    def __init__(self, url=None):
        super().__init__(url)
        self._url = url
        self._model = Wordpress
        self._exception_not_exist = WordpressDoesNotExistError

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
        except self._exception_not_exist as err:
            result.revoke()
            raise FakeNewsDoesNotExistError(_(str(err)))
        except FakeNewsDoesNotExistError as err:
            result.revoke()
            raise FakeNewsDoesNotExistError(_(str(err)))

    def _get_filename(self):
        return (self._get_fakenews()).post_type + '.csv'


# Soup #
class SoupResponseHandler(FakeNewsResponseHandler):

    def __init__(self, url=None, link_class=None, date_type=None, date_id=None):
        super().__init__(url)
        self._url = url
        self._link_class = link_class
        self._date_type = date_type
        self._date_id = date_id
        self._model = Soup
        self._exception_not_exist = SoupDoesNotExistError

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
        except self._exception_not_exist as err:
            result.revoke()
            raise FakeNewsDoesNotExistError(_(str(err)))
        except FakeNewsDoesNotExistError as err:
            result.revoke()
            raise FakeNewsDoesNotExistError(_(str(err)))

    def _get_filename(self):
        return urlparse(self._url).netloc + '.csv'