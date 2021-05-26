
from django.utils.translation import gettext as _
from .wordpress import(
    NoOKResponseError,
    TooManyRequestError
)

from .models import FakeNews, Post

# Custom Exceptions
class ResponseHandlerError(Exception):
    pass

class FakeNewsResponseHandler:

    def __init__(
        self,
        url=None
    ):
        self._url = url

    def handle_response(self):
        try:            
            self._handle()
        except (
                NoOKResponseError,
                TooManyRequestError,
                FakeNewsAlreadyExistError
            ) as err:
            raise ResponseHandlerError(_(str(err)))

    def handle_update_response(self):
        try:            
            self._update()
        except (
                NoOKResponseError,
                TooManyRequestError,
                FakeNewsDoesNotExistError
            ) as err:
            raise ResponseHandlerError(_(str(err)))

    def handle_download_response(self):
        try:            
            self._download()
        except (
                NoOKResponseError,
                TooManyRequestError,
                FakeNewsDoesNotExistError
            ) as err:
            raise ResponseHandlerError(_(str(err)))

    def _get_fakenews(self):
        fakenews_qs = FakeNews.objects.find_by_url(self._url)
        if not fakenews_qs.exists():
            # Raise a meaningful error to be catched by the client
            error_msg = (
                'No existe un FakeNews con esta url {} '
                'Por favor, pruebe otra consulta'
            ).format(self._url)

            raise FakeNewsDoesNotExistError(_(error_msg))

        return fakenews_qs.get()

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
                'Ya existe un Wordpress con esta url {} '
                'Por favor, pruebe otra consulta'
            ).format(self._url)

            raise FakeNewsAlreadyExistError(_(error_msg))

        return True

##### POST #####
# Custom Exceptions
class PostAlreadyExistError(Exception):
    pass

# PostResponse
class PostsResponseHandler:
    def __init__(
        self,
        url = None,
        fakenews_id = None
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