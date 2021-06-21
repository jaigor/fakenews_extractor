from django.utils.translation import gettext as _

from twitter.models import Query, Tweet, User


# Custom Exceptions
class QueryAlreadyExistError(Exception):
    pass


class QueryDoesNotExistError(Exception):
    pass


class TweetAlreadyExistError(Exception):
    pass


class UserAlreadyExistError(Exception):
    pass


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
        self.valid_data()
        return Query.objects.create_query(
            text=self._text,
        )


# Tweet #
class TweetRegister:

    def __init__(
            self,
            _id,
            text,
            conversation_id,
            created_at,
            author,
            lang=None,
    ):
        self._id = _id
        self._text = text
        self._conversation_id = conversation_id
        self._created_at = created_at
        self._lang = lang
        self._author = author

    def execute(self):
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
        self.valid_data()
        return Tweet.objects.create_tweet(
            _id=self._id,
            text=self._text,
            author=self._author,
            conversation_id=self._conversation_id,
            created_at=self._created_at,
            lang=self._lang)


# User #
class UserRegister:

    def __init__(
            self,
            _id,
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
        self._id = _id
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
        user = self._create_user()

        return user

    def valid_data(self):
        user_qs = User.objects.find_by_id(self._id)
        if user_qs.exists():
            error_msg = (
                'Ya existe un usuario con ese id {} '
                'Por favor, pruebe otro'
            ).format(self._id)

            raise UserAlreadyExistError(_(error_msg))

        return True

    def _create_user(self):
        self.valid_data()
        return User.objects.create_user(
            _id=self._id,
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
