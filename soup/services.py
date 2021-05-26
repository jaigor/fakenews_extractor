from django.utils.translation import gettext as _
from urllib.parse import urlparse

from .scrapper import(
    Scrapper, 
    NoOKResponseError,
    TooManyRequestError,
    NoSoupTypeError,
    NoLinksFoundError
)
from .models import Soup, Post

# Custom Exceptions
class ResponseHandlerError(Exception):
    pass
class SoupAlreadyExistError(Exception):
    pass
class SoupDoesNotExistError(Exception):
    pass
class PostAlreadyExistError(Exception):
    pass

# SoupResponse
class SoupResponseHandler:
    def __init__(
        self,
        url,
        link_class=None,
        date_type=None,
        date_id=None
    ):
        self._url = url
        self._link_class = link_class
        self._date_type = date_type
        self._date_id = date_id
        
    def handle_response(self):
        try:            
            # get all links
            links = self._get_external_links()
            # if no failure, register soup
            soup = self._register_new_soup()
            # register links
            self._register_links(links, soup)

        except (
                NoOKResponseError,
                TooManyRequestError,
                SoupAlreadyExistError,
                NoSoupTypeError,
                NoLinksFoundError
            ) as err:
            raise ResponseHandlerError(_(str(err)))

    def handle_update_response(self):
        try:            
            # get all links
            links = self._get_external_links()
            # get soup
            soup = self._get_soup()
            # update links
            self._register_links(links, soup)

        except (
                NoOKResponseError,
                TooManyRequestError,
                NoSoupTypeError,
                NoLinksFoundError,
                SoupDoesNotExistError
            ) as err:
            raise ResponseHandlerError(_(str(err)))     

    def handle_download_response(self):
        try:
            posts = self._get_internal_posts()
            filename = urlparse(self._url).netloc + '.csv'

            return Scrapper(self._url).get_csv_response(filename, posts)

        except (
                NoOKResponseError,
                TooManyRequestError,
                SoupAlreadyExistError                
            ) as err:
            raise ResponseHandlerError(_(str(err)))

    def _get_external_links(self):
        scrapper = Scrapper(self._url, 
                        self._link_class, 
                        self._date_type, 
                        self._date_id)
        return scrapper.get_collection()

    def _get_internal_posts(self):
        # valid data
        s = self._get_soup()
        return Soup.objects.get_posts(s.id)
    
    def _get_soup(self):
        soup_qs = Soup.objects.find_by_url(self._url)
        if not soup_qs.exists():
            # Raise a meaningful error to be catched by the client
            error_msg = (
                'No existe un Soup con esta url {} '
                'Por favor, pruebe otra consulta'
            ).format(self._url)

            raise SoupDoesNotExistError(_(error_msg))

        return soup_qs.get()

    def _register_links(self, links, soup):            
        scrapper = Scrapper(self._url, 
                            self._link_class, 
                            self._date_type, 
                            self._date_id)

        posts = scrapper.get_posts_content(links)
        for post in posts:
            # register each post [date, link, title, content]
            new_post = self._register_post(
                                post[0],
                                post[1],
                                post[2],
                                post[3])
            # and add to Soup
            Soup.objects.add_post(soup, new_post)

    def _register_new_soup(self):
        soup = SoupRegister(
            url=self._url,
            link_class=self._link_class,
            date_type=self._date_type,
            date_id=self._date_id,
        )
        return soup.execute()
    
    def _register_post(self, 
                        date,
                        link,
                        title,
                        content):
        post = PostRegister(
            date=date,
            link=link,
            title=title,
            content=content,
        )
        # exists = update
        if post.valid_post():
            return post.update()
        # create
        else:
            return post.execute()

# PostResponse
class PostsResponseHandler:
    def __init__(
        self,
        url = None,
        soup_id = None
    ):
        self._url = url
        self._soup_id = soup_id

    def get_queryset(self):
        try:  
            s = self._get_soup()
            return Soup.objects.get_post_queryset(s.id)
        except (
                NoOKResponseError,
                TooManyRequestError,
                SoupDoesNotExistError
            ) as err:
            raise ResponseHandlerError(_(str(err)))

    def _get_soup(self):
        soup_qs = Soup.objects.find_by_id(self._soup_id)
        if not soup_qs.exists():
            # Raise a meaningful error to be catched by the client
            error_msg = (
                'No existe un Scrapper con este id {} '
                'Por favor, pruebe otra consulta'
            ).format(self._soup_id)

            raise SoupDoesNotExistError(_(error_msg))

        return soup_qs.get()

class SoupRegister:

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

    def execute(self):
        self.valid_data()
        soup = self._create_soup()

        return soup

    def valid_data(self):
        soup_qs = Soup.objects.find_by_url(self._url)
        if soup_qs.exists():
            # Raise a meaningful error to be catched by the client
            error_msg = (
                'Ya existe un Soup con esta url {} '
                'Por favor, pruebe otra consulta'
            ).format(self._link)

            raise SoupAlreadyExistError(_(error_msg))

        return True

    def _create_soup(self):
        return Soup.objects.create_soup(
            self._url,
            self._link_class,
            self._date_type,
            self._date_id, 
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

    def update(self):
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