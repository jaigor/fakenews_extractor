from django.utils.translation import gettext as _
from .models import FakeNews, Post


# Custom Exceptions
class FakeNewsAlreadyExistError(Exception):
    pass


class FakeNewsDoesNotExistError(Exception):
    pass


class FakeNewsRegister:

    def __init__(
            self,
            url
    ):
        self._url = url
        self._model = FakeNews

    def execute(self):
        self.valid_data()
        fakenews = self._create_fakenews()

        return fakenews

    def valid_data(self):
        fakenews_qs = self._model.objects.find_by_url(self._url)
        if fakenews_qs.exists():
            # Raise a meaningful error to be catched by the client
            error_msg = (
                'Ya existe un FakeNews con esta url {} '
                'Por favor, pruebe otra consulta'
            ).format(self._url)

            raise FakeNewsAlreadyExistError(_(error_msg))

        return True

    def _create_fakenews(self):
        pass

    def update_fakenews(self):
        pass


# Custom Exceptions
class PostDoesNotExistError(Exception):
    pass


class PostAlreadyExistError(Exception):
    pass


class PostRegister:

    def __init__(
            self,
            date,
            link,
            title,
            content,
            source_urls
    ):
        self._date = date
        self._link = link
        self._title = title
        self._content = content
        self._source_urls = source_urls

    def execute(self):
        # exists = update
        if Post.objects.find_by_link(self._link).exists():
            self.update_post()
            return Post.objects.find_by_link(self._link).get()
        # create
        else:
            return self._create_post()

    def valid_data(self):
        post_qs = Post.objects.find_by_link(self._link)
        if post_qs.exists():
            # Raise a meaningful error to be catched by the client
            error_msg = (
                'Ya existe un post igual con el link {} '
                'Por favor, pruebe otra consulta'
            ).format(self._link)

            raise PostAlreadyExistError(_(error_msg))

        return True

    def _create_post(self):
        self.valid_data()
        return Post.objects.create_post(
            date=self._date,
            link=self._link,
            title=self._title,
            content=self._content,
            urls=self._source_urls
        )

    def update_post(self):
        self.valid_post()
        Post.objects.update_post(
            date=self._date,
            link=self._link,
            title=self._title,
            content=self._content,
            urls=self._source_urls
        )

    def valid_post(self):
        post_qs = Post.objects.find_by_link(self._link)
        if not post_qs.exists():
            # Raise a meaningful error to be catched by the client
            error_msg = (
                'No existe un post igual con el link {} '
                'Por favor, pruebe otra consulta'
            ).format(self._link)

            raise PostDoesNotExistError(_(error_msg))

        return True
