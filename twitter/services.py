from django.utils.translation import gettext as _

from .models import (
    Tweet,
    User,
    Query
)
from .twitter import (
    TweetLookup,
    UserLookup,
    TweetsRequestError,
    UserRequestError
)


# Custom Exceptions 
class ResponseHandlerError(Exception):
    pass


class QueryAlreadyExistError(Exception):
    pass


class QueryDoesNotExistError(Exception):
    pass


class TweetAlreadyExistError(Exception):
    pass


class UserAlreadyExistError(Exception):
    pass


# Response
class ResponseHandler:

    def __init__(
            self,
            query
    ):
        self._query = query

    def handle_response(self):
        # handle different outputs
        try:
            # query registration
            self._register_new_query()
            # search on external API for tweets
            tweets = self._get_tweets_response()
            # register tweets
            self._register_tweets(tweets)
        except (
                QueryAlreadyExistError,
                TweetsRequestError,
                TweetAlreadyExistError,
                UserRequestError,
                UserAlreadyExistError
        ) as err:
            raise ResponseHandlerError(_(str(err)))

    def handle_update_response(self):
        # handle different outputs
        try:
            # get query
            query = self._get_query()
            # search on external API for tweets
            tweets = self._get_tweets_response()
            # register tweets
            self._register_tweets(tweets)
        except (
                QueryDoesNotExistError,
                TweetsRequestError,
                TweetAlreadyExistError,
                UserRequestError,
                UserAlreadyExistError
        ) as err:
            raise ResponseHandlerError(_(str(err)))

    def handle_download_response(self):
        try:
            tweets = self._get_internal_tweets()
            filename = self._query + '.csv'

            headers = ['text', 'author', 'conversation_id', 'created_at', 'lang']
            return TweetLookup(self._query).get_csv_response(filename, tweets, headers)
        except (
                QueryDoesNotExistError
        ) as err:
            raise ResponseHandlerError(_(str(err)))

    def get_tweet_queryset(self):
        try:
            q = self._get_query()
            return Query.objects.get_tweet_queryset(q.id)
        except (
                QueryDoesNotExistError
        ) as err:
            raise ResponseHandlerError(_(str(err)))

    def _get_internal_tweets(self):
        # valid data
        q = self._get_query()
        return Query.objects.get_tweets(q.id)

    def _get_tweets_response(self):
        twitter = TweetLookup(self._query)
        return twitter.search_tweets()

    def _get_user_response(self, author_id):
        twitter = UserLookup(author_id)
        return twitter.search_user()

    def _get_query(self):
        query_qs = Query.objects.find_by_text(self._query)
        if not query_qs.exists():
            # Raise a meaningful error to be cached by the client
            error_msg = (
                'No existe una Query con este texto {} '
                'Por favor, pruebe otra consulta'
            ).format(self._query)

            raise QueryDoesNotExistError(_(error_msg))

        return query_qs.get()

    def _fill_field(self, dict, attr):
        try:
            return dict[attr]
        except KeyError:
            return None

    def _register_new_query(self):
        register = QueryRegister(
            self._query
        )
        register.execute()

    def _register_new_user(self, author_id):
        user_response = self._get_user_response(author_id)
        # create new one
        # fields that can not be returned
        description = self._fill_field(user_response, 'description')
        location = self._fill_field(user_response, 'location')
        url = self._fill_field(user_response, 'url')

        user = UserRegister(
            id=user_response['id'],
            name=user_response['name'],
            username=user_response['username'],
            created_at=user_response['created_at'],
            profile_image_url=user_response['profile_image_url'],
            protected=user_response['protected'],
            public_metrics=user_response['public_metrics'],
            verified=user_response['verified'],
            description=description,
            location=location,
            url=url,
            tweet_id=None
        )
        user.execute()

    def _register_new_tweet(self, t):
        # create tweet
        tweet = TweetRegister(
            id=t['id'],
            text=t['text'],
            conversation_id=t['conversation_id'],
            created_at=t['created_at'],
            lang=t['lang'],
            author_id=None
        )
        tweet.execute()

    def _register_tweets(self, tweets):
        for t in tweets:
            # get or create tweet
            tweet_id = t['id']
            tweet_qs = Tweet.objects.find_by_id(tweet_id)
            if tweet_qs.exists():
                print("Ya existe un tweet con ese id")
            else:
                # get or create user
                author_id = t['author_id']
                user = User.objects.find_by_id(author_id)
                if not user.exists():
                    self._register_new_user(author_id)

                # create tweet
                self._register_new_tweet(t)

                # link user to tweet
                user = User.objects.find_by_id(author_id)
                Tweet.objects.add_author(tweet_id, user)

                # link tweet to the users list
                tweet_qs = Tweet.objects.find_by_id(tweet_id)
                User.objects.add_tweet(author_id, tweet_qs.get())

            # add existent or new tweet to query
            Query.objects.add_tweet(self._query, tweet_qs.get())


# Query #
class QueryRegister:

    def __init__(
            self,
            text,
            tweet_id=None,
    ):
        self._text = text
        self._tweet_id = tweet_id

    def execute(self):
        self.valid_data()
        query = self._create_query()

        return query

    def valid_data(self):
        query_qs = Query.objects.find_by_text(self._text)
        if query_qs.exists():
            error_msg = (
                'Ya existe una consulta igual con el texto {} '
                'Por favor, pruebe otra consulta'
            ).format(self._text)

            raise QueryAlreadyExistError(_(error_msg))

        return True

    # private methods
    def _create_query(self):
        query = Query.objects.create(
            text=self._text,
        )
        query.save()
        return query


# Tweet #
class TweetRegister:

    def __init__(
            self,
            id,
            text,
            conversation_id,
            created_at,
            lang=None,
            author_id=None
    ):
        self._id = id
        self._text = text
        self._conversation_id = conversation_id
        self._created_at = created_at
        self._lang = lang
        self._author_id = author_id

    def execute(self):
        self.valid_data()
        tweet = self._create_tweet()

        return tweet

    def valid_data(self):
        tweet_qs = Tweet.objects.find_by_id(self._id)
        if tweet_qs.exists():
            error_msg = (
                'Ya existe un tweet con ese id {} '
                'Por favor, pruebe otro'
            ).format(self._id)

            raise TweetAlreadyExistError(_(error_msg))

        return True

    def _create_tweet(self):
        tweet = Tweet.objects.create(id=self._id,
                                     text=self._text,
                                     author_id=self._author_id,
                                     conversation_id=self._conversation_id,
                                     created_at=self._created_at,
                                     lang=self._lang)
        tweet.save()
        return tweet


# User #
class UserRegister:

    def __init__(
            self,
            id,
            name,
            username,
            created_at,
            profile_image_url,
            protected,
            public_metrics,
            verified,
            description=None,
            location=None,
            url=None,
            tweet_id=None
    ):
        self._id = id
        self._name = name
        self._username = username
        self._created_at = created_at
        self._profile_image_url = profile_image_url
        self._protected = protected
        self._public_metrics = public_metrics
        self._verified = verified
        self._description = description
        self._location = location
        self._url = url
        self._tweet_id = tweet_id

    def execute(self):
        self.valid_data()
        user = self._create_user()

        return user

    def valid_data(self):
        user_qs = User.objects.find_by_id(self._id)
        if user_qs.exists():
            error_msg = (
                'Ya existe un usuario con ese id {} '
                'Por favor, pruebe otro'
            ).format(self._id)

            raise TweetAlreadyExistError(_(error_msg))

        return True

    def _create_user(self):
        user = User.objects.create(id=self._id,
                                   name=self._name,
                                   username=self._username,
                                   created_at=self._created_at,
                                   description=self._description,
                                   location=self._location,
                                   profile_image_url=self._profile_image_url,
                                   protected=self._protected,
                                   public_metrics=self._public_metrics,
                                   url=self._url,
                                   verified=self._verified)
        user.save()
        return user
