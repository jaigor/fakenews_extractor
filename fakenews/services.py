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

    def __init__(self,
                 url=None,
                 f_source_type=None,
                 f_source_pattern=None,
                 f_source_entire_link=None,

                 s_source_type=None,
                 s_source_pattern=None,
                 s_source_entire_link=None,
                 ):
        super().__init__(url,
                         f_source_type, f_source_pattern, f_source_entire_link,
                         s_source_type, s_source_pattern, s_source_entire_link)
        self._url = url
        self._model = Wordpress
        self._exception_not_exist = WordpressDoesNotExistError

    def _handle(self):
        result = None
        try:
            result = chain(get_wordpress_urls.s(self._url, False),
                           register_wordpress_list_posts.s(self._f_source_pattern, self._f_source_type,
                                                           self._f_source_entire_link,
                                                           self._s_source_pattern, self._s_source_type,
                                                           self._s_source_entire_link)).apply_async()
            propagate_chain_get(result)
            return result
        except (WordpressAlreadyExistError, FakeNewsAlreadyExistError) as err:
            result.revoke()
            raise FakeNewsAlreadyExistError(_(str(err)))

    def _update(self):
        result = None
        try:
            result = chain(get_wordpress_urls.s(self._url, True),
                           register_wordpress_list_posts.s(self._f_source_pattern, self._f_source_type,
                                                           self._f_source_entire_link,
                                                           self._s_source_pattern, self._s_source_type,
                                                           self._s_source_entire_link)).apply_async()
            propagate_chain_get(result)
            return result
        except (self._exception_not_exist, FakeNewsDoesNotExistError) as err:
            result.revoke()
            raise FakeNewsDoesNotExistError(_(str(err)))

    def _get_filename(self):
        return (self._get_fakenews()).post_type + '.csv'


# Soup #
class SoupResponseHandler(FakeNewsResponseHandler):

    def __init__(self,
                 url=None,
                 f_source_type=None,
                 f_source_pattern=None,
                 f_source_entire_link=None,

                 s_source_type=None,
                 s_source_pattern=None,
                 s_source_entire_link=None,

                 link_class=None,
                 date_type=None,
                 date_id=None,
                 body_class=None):
        super().__init__(url,
                         f_source_type, f_source_pattern, f_source_entire_link,
                         s_source_type, s_source_pattern, s_source_entire_link)
        self._url = url
        self._link_class = link_class
        self._date_type = date_type
        self._date_id = date_id
        self._body_class = body_class
        self._model = Soup
        self._exception_not_exist = SoupDoesNotExistError

    def _handle(self):
        result = None
        try:
            result = register_soup_posts.s(
                False, self._url, self._link_class, self._date_type, self._date_id, self._body_class,
                self._f_source_pattern, self._f_source_type,
                self._f_source_entire_link,
                self._s_source_pattern, self._s_source_type,
                self._s_source_entire_link).apply_async()
            return result
        except (SoupAlreadyExistError, FakeNewsAlreadyExistError) as err:
            result.revoke()
            raise FakeNewsAlreadyExistError(_(str(err)))

    def _update(self):
        result = None
        try:
            result = register_soup_posts.s(
                True, self._url, self._link_class, self._date_type, self._date_id, self._body_class,
                self._f_source_pattern, self._f_source_type,
                self._f_source_entire_link,
                self._s_source_pattern, self._s_source_type,
                self._s_source_entire_link).apply_async()
            return result
        except (self._exception_not_exist, FakeNewsDoesNotExistError) as err:
            result.revoke()
            raise FakeNewsDoesNotExistError(_(str(err)))

    def _get_filename(self):
        return urlparse(self._url).netloc + '.csv'
