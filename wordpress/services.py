from django.utils.translation import gettext as _
from urllib.parse import urlparse
from .wordpress import(
    WordpressAPI, 
    NoOKResponseError,
    TooManyRequestError
)

from .models import Wordpress, Post

# Custom Exceptions
class ResponseHandlerError(Exception):
    pass
class WordpressAlreadyExistError(Exception):
    pass
class WordpressDoesNotExistError(Exception):
    pass
class PostAlreadyExistError(Exception):
    pass
class PostDoesNotExistError(Exception):
    pass

# TypesResponse
class TypesResponseHandler:
    def __init__(
        self,
        url
    ):
        self._url = url
        
    def handle_types_response(self):
        try:            
            # get types of posts
            types = self._get_types()
            for k, v in types.items():
                # register wordpress
                self._register_new_wordpress(v,k)

        except (
                NoOKResponseError,
                TooManyRequestError,
                WordpressAlreadyExistError                
            ) as err:
            raise ResponseHandlerError(_(str(err)))

    def _register_new_wordpress(self, url, post_type):
        register = WordpressRegister(
            url=url,
            post_type=post_type
        )
        # exists = update
        if Wordpress.objects.find_by_url(self._url).exists():
            register.update_post()
            return Wordpress.objects.find_by_url(self._url).get()
        # create
        else:
            return register.execute()

    def _get_types(self):
        #print("types " + self._url)
        wordpress = WordpressAPI(self._url)
        return wordpress.get_posts_types()

# PostResponse
class PostsResponseHandler:
    def __init__(
        self,
        url = None,
        wordpress_id = None
    ):
        self._url = url
        self._wordpress_id = wordpress_id
        
    def handle_post_response(self):
        try:
            posts = self._get_external_posts()
            # get wordpress to link posts
            w = self._get_wordpress()

            for post in posts:
                # register each post [date, link, title, content]
                new_post = self._register_post(
                                            post[0],
                                            post[1],
                                            post[2],
                                            post[3])
                # and add to wordpress
                Wordpress.objects.add_post(w, new_post)

        except (
                NoOKResponseError,
                TooManyRequestError,                
                PostAlreadyExistError,
                WordpressDoesNotExistError
            ) as err:
            raise ResponseHandlerError(_(str(err)))

    def handle_download_response(self):
        try:
            posts = self._get_internal_posts()
            w = self._get_wordpress()
            filename = w.post_type + '.csv'
            return WordpressAPI(self._url).get_csv_response(filename, posts)
        except (
                NoOKResponseError,
                TooManyRequestError,
                WordpressDoesNotExistError
            ) as err:
            raise ResponseHandlerError(_(str(err)))
    
    def get_queryset(self):
        try:
            w = self._get_wordpress()
            return Wordpress.objects.get_post_queryset(w.id)
        except (WordpressDoesNotExistError
            ) as err:
            raise ResponseHandlerError(_(str(err)))

    def _get_wordpress(self):
        wordpress_qs = Wordpress.objects.find_by_id(self._wordpress_id)
        if not wordpress_qs.exists():
            # Raise a meaningful error to be catched by the client
            error_msg = (
                'No existe un Wordpress con este id {} '
                'Por favor, pruebe otra consulta'
            ).format(self._wordpress_id)

            raise WordpressDoesNotExistError(_(error_msg))

        return wordpress_qs.get()

    def _get_external_posts(self):
        wordpress = WordpressAPI(self._url)
        return wordpress.get_posts_content(self._url)

    def _get_internal_posts(self):
        # valid data
        w = self._get_wordpress()
        return Wordpress.objects.get_posts(w.id)

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

class WordpressRegister:

    def __init__(
        self,
        url,
        post_type=None
    ):
        self._url = url
        self._post_type = post_type
        self._domain = urlparse(self._url).netloc

    def execute(self):
        self.valid_data()  
        wordpress = self._create_wordpress()

        return wordpress

    def valid_data(self):
        wordpress_qs = Wordpress.objects.find_by_url(self._url)
        if wordpress_qs.exists():
            # Raise a meaningful error to be catched by the client
            error_msg = (
                'Ya existe un Wordpress con esta url {} '
                'Por favor, pruebe otra consulta'
            ).format(self._url)

            raise WordpressAlreadyExistError(_(error_msg))

        return True

    def _create_wordpress(self):
        return Wordpress.objects.create_wordpress(
            url=self._url,
            post_type=self._post_type,
            domain=self._domain,
            )

    def update_wordpress(self):
        return Wordpress.objects.update_wordpress(
            url=self.url,
            post_type=self._post_type,
            domain=self._domain,
            )

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
        return Post.objects.update_post(
            date=self._date,
            link=self._link,
            title=self._title,
            content=self._content,
            )