from django.utils.translation import gettext as _

from .csvDownloader import CsvDownloader
from .wordpress import (
    NoOKResponseError,
    TooManyRequestError
)
from .models import FakeNews, Post
from .base_register import PostRegister, PostAlreadyExistError


# Custom Exceptions
class ResponseHandlerError(Exception):
    pass


class FakeNewsResponseHandler:

    def __init__(
            self,
            url=None
    ):
        self._url = url
        self._model = FakeNews
        self._exception_not_exist = FakeNewsDoesNotExistError
        self._filename = "data.csv"

    def handle_response(self):
        try:
            return self._handle()
        except (
                NoOKResponseError,
                TooManyRequestError,
                FakeNewsAlreadyExistError
        ) as err:
            raise ResponseHandlerError(_(str(err)))

    def handle_update_response(self):
        try:
            return self._update()
        except (
                NoOKResponseError,
                TooManyRequestError,
                FakeNewsDoesNotExistError
        ) as err:
            raise ResponseHandlerError(_(str(err)))

    def handle_download_response(self):
        try:
            return self._download()
        except (
                NoOKResponseError,
                TooManyRequestError,
                FakeNewsDoesNotExistError
        ) as err:
            raise ResponseHandlerError(_(str(err)))

    def get_queryset(self, _id):
        try:
            return self._model.objects.get_post_queryset(_id)
        except self._exception_not_exist as err:
            raise FakeNewsDoesNotExistError(_(str(err)))

    def _get_fakenews(self):
        fakenews_qs = self._model.objects.find_by_url(self._url)
        if not fakenews_qs.exists():
            # Raise a meaningful error to be catched by the client
            error_msg = (
                'No existe un FakeNews con esta url {} '
                'Por favor, pruebe otra consulta'
            ).format(self._url)

            raise self._exception_not_exist(_(error_msg))

        return fakenews_qs.get()

    def _get_internal_posts(self):
        # valid data
        fakenews = self._get_fakenews()
        return self._model.objects.get_posts(fakenews.id)

    def _handle(self):
        pass

    def _update(self):
        pass

    def _download(self):
        try:
            posts = self._get_internal_posts()
            return CsvDownloader().get_csv_response(self._get_filename(), posts)
        except self._exception_not_exist as err:
            raise FakeNewsDoesNotExistError(_(str(err)))

    def _get_filename(self):
        pass


# Custom Exceptions
class FakeNewsAlreadyExistError(Exception):
    pass


class FakeNewsDoesNotExistError(Exception):
    pass


# POST #
# PostResponse
class PostsResponseHandler:
    def __init__(
            self,
            url=None,
            fakenews_id=None
    ):
        self._url = url
        self._fakenews_id = fakenews_id

    def handle_post_response(self, fakenews, posts):
        try:
            for post in posts:
                # register each post [date, link, title, content]
                new_post = self._register_post(
                    post[0],
                    post[1],
                    post[2],
                    post[3])
                # and add to fakenews
                FakeNews.objects.add_post(fakenews, new_post)
        except (
                NoOKResponseError,
                TooManyRequestError,
                PostAlreadyExistError
        ) as err:
            raise ResponseHandlerError(_(str(err)))

    def _get_fakenews(self):
        fakenews_qs = FakeNews.objects.find_by_id(self._fakenews_id)
        if not fakenews_qs.exists():
            # Raise a meaningful error to be catched by the client
            error_msg = (
                'No existe una FakeNews con este id {} '
                'Por favor, pruebe otra consulta'
            ).format(self._fakenews_id)

            raise FakeNewsDoesNotExistError(_(error_msg))

        return fakenews_qs.get()

    def _register_post(self, date, link, title, content):
        register = PostRegister(
            date=date,
            link=link,
            title=title,
            content=content
        )
        # exists = update
        if Post.objects.find_by_link(link).exists():
            register.update_post()
            return Post.objects.find_by_link(link).get()
        # create
        else:
            return register.execute()
