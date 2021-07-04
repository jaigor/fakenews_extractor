from .base_register import FakeNewsRegister
from urllib.parse import urlparse
from .models import Wordpress, Soup


class WordpressRegister(FakeNewsRegister):

    def __init__(self, url, post_type=None):
        super().__init__(url)
        self._url = url
        self._post_type = post_type
        self._domain = urlparse(self._url).netloc
        self._model = Wordpress

    def _create_fakenews(self):
        return self._model.objects.create_wordpress(
            url=self._url,
            post_type=self._post_type,
            domain=self._domain,
        )

    def update_fakenews(self):
        return self._model.objects.update_wordpress(
            url=self._url,
            post_type=self._post_type,
            domain=self._domain,
        )


class SoupRegister(FakeNewsRegister):

    def __init__(self, url, link_class, date_type, date_id, body_class=None):
        super().__init__(url)
        self._url = url
        self._link_class = link_class
        self._date_type = date_type
        self._date_id = date_id
        self._body_class = body_class
        self._model = Soup

    def _create_fakenews(self):
        return Soup.objects.create_soup(
            self._url,
            self._link_class,
            self._date_type,
            self._date_id,
            self._body_class
        )

    def update_fakenews(self):
        return Soup.objects.update_soup(
            self._url,
            self._link_class,
            self._date_type,
            self._date_id,
            self._body_class
        )
