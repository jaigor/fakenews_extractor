from fakenews.models import Post
from django.utils.translation import gettext as _

from twitter.services import ResponseHandlerError, ResponseHandler


class FakeNewsHandler:

    def __init__(
            self,
            id=None
    ):
        self._id = id

    def handle_search_response(self):

        # check which source (text or urls)
        post_qs = Post.objects.find_by_id(self._id)
        if not post_qs.exists():
            # Raise a meaningful error to be cached by the client
            error_msg = (
                'No existe un Post con este id {} \n'
                '. Por favor, pruebe otra consulta'
            ).format(self._id)

            raise ResponseHandlerError(_(error_msg))
        else:
            post = post_qs.get()

        # if text process normal
        if post.fake_news_sources is None or post.fake_news_sources == []:
            query = post.title
            # handle the output
            handler = ResponseHandler(
                query
            )
            return handler.handle_response()

        # else iterate through urls
        else:
            for url in post.fake_news_sources:
                print(url)
                try:
                    handler = ResponseHandler(
                        url
                    )
                    return handler.handle_response()
                except ResponseHandlerError as err:
                    # ignore errors in order to continue
                    pass