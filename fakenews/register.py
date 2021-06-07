from .base_services import FakeNewsRegister
from urllib.parse import urlparse
from .models import Wordpress, Soup


class WordpressDoesNotExistError(Exception):
    pass


class WordpressAlreadyExistError(Exception):
    pass


class WordpressRegister(FakeNewsRegister):

    def __init__(self, url, post_type=None):
        super().__init__(url)
        self._url = url
        self._post_type = post_type
        self._domain = urlparse(self._url).netloc

    def _create_fakenews(self):
        return Wordpress.objects.create_wordpress(
            url=self._url,
            post_type=self._post_type,
            domain=self._domain,
        )

    def update_fakenews(self):
        return Wordpress.objects.update_wordpress(
            url=self._url,
            post_type=self._post_type,
            domain=self._domain,
        )


class SoupDoesNotExistError(Exception):
    pass


class SoupAlreadyExistError(Exception):
    pass


class SoupRegister(FakeNewsRegister):

    def __init__(self, url, link_class, date_type, date_id):
        super().__init__(url)
        self._url = url
        self._link_class = link_class
        self._date_type = date_type
        self._date_id = date_id

    def _create_fakenews(self):
        return Soup.objects.create_soup(
            self._url,
            self._link_class,
            self._date_type,
            self._date_id,
        )

    def update_fakenews(self):
        return Soup.objects.update_soup(
            self._url,
            self._link_class,
            self._date_type,
            self._date_id,
        )
