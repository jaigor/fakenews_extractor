from django.utils.translation import gettext as _
from urllib.parse import urlparse

from .wordpress import WordpressAPI
from .scrapper import Scrapper

from .models import Wordpress, Soup
from .base_services import (
    FakeNewsRegister,
    FakeNewsResponseHandler,
    PostsResponseHandler,
    FakeNewsAlreadyExistError,
    FakeNewsDoesNotExistError
)


# Custom Exceptions
class WordpressAlreadyExistError(Exception):
    pass


class WordpressDoesNotExistError(Exception):
    pass


class PostAlreadyExistError(Exception):
    pass


class PostDoesNotExistError(Exception):
    pass


# Wordpress #
class WordpressResponseHandler(FakeNewsResponseHandler):

    def get_queryset(self, id):
        try:
            return Wordpress.objects.get_post_queryset(id)
        except WordpressDoesNotExistError as err:
            raise FakeNewsDoesNotExistError(_(str(err)))

    def _handle(self):
        try:
            self._register_response(False)
        except WordpressAlreadyExistError as err:
            raise FakeNewsAlreadyExistError(_(str(err)))

    def _update(self):
        try:
            self._register_response(True)
        except WordpressDoesNotExistError as err:
            raise FakeNewsDoesNotExistError(_(str(err)))

    def _download(self):
        try:
            posts = self._get_internal_posts()
            w = self._get_fakenews()
            filename = w.post_type + '.csv'
            return WordpressAPI(self._url).get_csv_response(filename, posts)
        except WordpressDoesNotExistError as err:
            raise FakeNewsDoesNotExistError(_(str(err)))

    ###
    def _register_response(self, is_update):

        if is_update:
            # get soup
            wordpress = self._get_wordpress()

            posts = self._get_external_posts(self._url)
            # register posts
            # delegate postresponsehandler
            post_handler = PostsResponseHandler()
            post_handler.handle_post_response(wordpress, posts)

        else:
            # get types of posts
            types = self._get_types()
            # if no failure, register wordpress
            for k, v in types.items():
                # register wordpress
                wordpress = self._register_new_wordpress(v, k)

                posts = self._get_external_posts(v)
                # register posts
                # delegate postresponsehandler
                post_handler = PostsResponseHandler()
                post_handler.handle_post_response(wordpress, posts)

    def _get_types(self):
        wordpress = WordpressAPI(self._url)
        return wordpress.get_posts_types()

    def _register_new_wordpress(self, url, post_type):
        register = WordpressRegister(
            url=url,
            post_type=post_type
        )
        return register.execute()

    def _get_wordpress(self):
        fakenews_qs = Wordpress.objects.find_by_url(self._url)
        if not fakenews_qs.exists():
            # Raise a meaningful error to be cached by the client
            error_msg = (
                'No existe un Wordpress con esta url {} '
                'Por favor, pruebe otra consulta'
            ).format(self._url)

            raise WordpressDoesNotExistError(_(error_msg))

        return fakenews_qs.get()

    def _get_external_posts(self, post_type_url):
        wordpress = WordpressAPI(post_type_url)
        return wordpress.get_posts_content(post_type_url)

    def _get_internal_posts(self):
        # valid data
        w = self._get_fakenews()
        return Wordpress.objects.get_posts(w.id)


class WordpressRegister(FakeNewsRegister):

    def __init__(
            self,
            url,
            post_type=None
    ):
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
            url=self.url,
            post_type=self._post_type,
            domain=self._domain,
        )


# Soup #
class SoupDoesNotExistError(Exception):
    pass


class SoupAlreadyExistError(Exception):
    pass


class SoupResponseHandler(FakeNewsResponseHandler):

    def __init__(
            self,
            url=None,
            link_class=None,
            date_type=None,
            date_id=None
    ):
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
        try:
            self._register_response(False)
        except SoupAlreadyExistError as err:
            raise FakeNewsAlreadyExistError(_(str(err)))

    def _update(self):
        try:
            self._register_response(True)
        except SoupDoesNotExistError as err:
            raise FakeNewsDoesNotExistError(_(str(err)))

    def _download(self):
        try:
            posts = self._get_internal_posts()
            filename = urlparse(self._url).netloc + '.csv'

            return Scrapper(self._url).get_csv_response(filename, posts)
        except SoupDoesNotExistError as err:
            raise FakeNewsDoesNotExistError(_(str(err)))

    ###
    def _register_response(self, is_update):
        # get all links
        links = self._get_external_links()
        # if no failure, register soup
        if is_update:
            # get soup
            soup = self._get_fakenews()
        else:
            soup = self._register_new_soup()

        # register links
        posts = self._get_external_posts(links)

        # register posts
        # delegate postresponsehandler
        post_handler = PostsResponseHandler()
        post_handler.handle_post_response(soup, posts)

    def _register_new_soup(self):
        soup = SoupRegister(
            url=self._url,
            link_class=self._link_class,
            date_type=self._date_type,
            date_id=self._date_id,
        )
        return soup.execute()

    def _get_external_links(self):
        scrapper = Scrapper(self._url,
                            self._link_class,
                            self._date_type,
                            self._date_id)
        return scrapper.get_collection()

    def _get_external_posts(self, links):
        scrapper = Scrapper(self._url,
                            self._link_class,
                            self._date_type,
                            self._date_id)

        return scrapper.get_posts_content(links)

    def _get_internal_posts(self):
        # valid data
        s = self.post_type()
        return Soup.objects.get_posts(s.id)


class SoupRegister(FakeNewsRegister):

    def __init__(
            self,
            url,
            link_class,
            date_type,
            date_id
    ):
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
