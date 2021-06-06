from .base_services import FakeNewsRegister
from urllib.parse import urlparse
from .models import Wordpress, Soup


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
