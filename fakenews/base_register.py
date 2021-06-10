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

    def execute(self):
        self.valid_data()
        fakenews = self._create_fakenews()

        return fakenews

    def valid_data(self):
        fakenews_qs = FakeNews.objects.find_by_url(self._url)
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
class PostAlreadyExistError(Exception):
    pass


class PostRegister:

    def __init__(
            self,
            date,
            link,
            title,
            content
    ):
        self._date = date
        self._link = link
        self._title = title
        self._content = content

    def execute(self):
        self.valid_data()
        post = self._create_post()

        return post

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
        return Post.objects.create_post(
            date=self._date,
            link=self._link,
            title=self._title,
            content=self._content,
        )

    def update_post(self):
        self.valid_post()
        self._update_post()

    def valid_post(self):
        post_qs = Post.objects.find_by_link(self._link)
        return post_qs.exists()

    def _update_post(self):
        Post.objects.find_by_link(self._link).update(
            date=self._date,
            link=self._link,
            title=self._title,
            content=self._content,
        )
