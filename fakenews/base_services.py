from django.utils.translation import gettext as _

from pages.downloader import Downloader
from .models import FakeNews
from .base_register import (
    PostRegister,
    PostAlreadyExistError,
    FakeNewsDoesNotExistError,
    FakeNewsAlreadyExistError, PostDoesNotExistError
)


# Custom Exceptions
class ResponseHandlerError(Exception):
    pass


class FakeNewsResponseHandler:

    def __init__(
            self,
            url=None,
            f_source_type=None,
            f_source_pattern=None,
            f_source_entire_link=None,

            s_source_type=None,
            s_source_pattern=None,
            s_source_entire_link=None,
    ):
        self._url = url
        self._model = FakeNews
        self._exception_not_exist = FakeNewsDoesNotExistError
        self._filename = "data.csv"
        self._f_source_type = f_source_type
        self._f_source_pattern = f_source_pattern
        self._f_source_entire_link = f_source_entire_link
        self._s_source_type = s_source_type
        self._s_source_pattern = s_source_pattern
        self._s_source_entire_link = s_source_entire_link

    def handle_response(self):
        try:
            return self._handle()
        except (
                FakeNewsAlreadyExistError
        ) as err:
            raise ResponseHandlerError(_(str(err)))

    def handle_update_response(self):
        try:
            return self._update()
        except (
                FakeNewsDoesNotExistError
        ) as err:
            raise ResponseHandlerError(_(str(err)))

    def handle_download_response(self):
        try:
            filename = self._get_filename()
            posts = self._get_internal_posts()
            headers = ['date', 'link', 'title', 'content']

            return Downloader().get_csv_response(filename, posts, headers)
        except (
                FakeNewsDoesNotExistError,
                self._exception_not_exist
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
        try:
            # valid data
            fakenews = self._get_fakenews()
            return self._model.objects.get_posts(fakenews.id)
        except self._exception_not_exist as err:
            raise FakeNewsDoesNotExistError(_(str(err)))

    def _handle(self):
        pass

    def _update(self):
        pass

    def _get_filename(self):
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
                # register each post [date, link, title, content, [fake_news_urls]]
                new_post = self._register_post(
                    post[0],
                    post[1],
                    post[2],
                    post[3],
                    post[4])
                # and add to fakenews
                FakeNews.objects.add_post(fakenews, new_post)
        except (
                PostAlreadyExistError,
                PostDoesNotExistError
        ) as err:
            raise ResponseHandlerError(_(str(err)))

    def _register_post(self, date, link, title, content, urls):
        register = PostRegister(
            date=date,
            link=link,
            title=title,
            content=content,
            source_urls=urls
        )
        return register.execute()