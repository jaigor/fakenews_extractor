from celery import chain
from django.utils.translation import gettext as _

from pages.downloader import Downloader
from .models import (
    Query
)
from .register import (
    QueryAlreadyExistError,
    QueryDoesNotExistError,
    QueryRegister
)
from .tasks import (
    get_tweets_response,
    register_tweets,
    TaskHandlerError
)


# Custom Exceptions 
class ResponseHandlerError(Exception):
    pass


# chain propagator
def propagate_chain_get(terminal_node, timeout=None):
    node = terminal_node.parent
    while node:
        node.get(propagate=True, timeout=timeout)
        node = node.parent


# Response
class ResponseHandler:

    def __init__(
            self,
            query=None
    ):
        self._query = query

    def handle_response(self):
        # handle different outputs
        try:
            # query registration
            self._register_new_query()
            # search on external API for tweets
            # register tweets
            result = chain(get_tweets_response.s(self._query),
                           register_tweets.s(self._query)).apply_async()
            propagate_chain_get(result)
            return result
        except (
                TaskHandlerError,
                QueryAlreadyExistError
        ) as err:
            raise ResponseHandlerError(_(str(err)))

    def handle_update_response(self):
        # handle different outputs
        try:
            # get query
            query = self._get_query()
            # search on external API for tweets
            # register tweets
            result = chain(get_tweets_response.s(self._query),
                           register_tweets.s(self._query)).apply_async()
            propagate_chain_get(result)
            return result
        except (
                TaskHandlerError,
                QueryDoesNotExistError
        ) as err:
            raise ResponseHandlerError(_(str(err)))

    def handle_download_response(self):
        try:
            filename = self._get_filename()
            tweets = self._get_internal_tweets()
            headers = ['text', 'author', 'conversation_id', 'created_at', 'lang']

            return Downloader().get_csv_response(filename, tweets, headers)
        except (
                QueryDoesNotExistError
        ) as err:
            raise ResponseHandlerError(_(str(err)))

    def handle_search_response(self):
        # handle the output
        return self.handle_response()

    def get_queryset(self, _id):
        try:
            return Query.objects.get_tweet_queryset(_id)
        except (
                QueryDoesNotExistError
        ) as err:
            raise ResponseHandlerError(_(str(err)))

    def _get_internal_tweets(self):
        # valid data
        q = self._get_query()
        return Query.objects.get_tweets(q.id)

    def _get_filename(self):
        return self._query + '.csv'

    def _get_query(self):
        query_qs = Query.objects.find_by_text(self._query)
        if not query_qs.exists():
            # Raise a meaningful error to be cached by the client
            error_msg = (
                'No existe una Query con este texto {} \n'
                '. Por favor, pruebe otra consulta'
            ).format(self._query)

            raise QueryDoesNotExistError(_(error_msg))

        return query_qs.get()

    def _register_new_query(self):
        register = QueryRegister(
            self._query
        )
        register.execute()
