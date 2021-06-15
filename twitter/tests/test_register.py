from django.test import TestCase
from django_mock_queries.query import MockSet
from mock import patch
import pytest

from twitter.models import Query, Tweet, User
from twitter.register import (
    QueryAlreadyExistError,
    QueryRegister,
    TweetRegister,
    TweetAlreadyExistError,
    UserAlreadyExistError,
    UserRegister
)


class TestQueryValidData(TestCase):
    qs_mock = MockSet(
        Query(
            text="query"
        )
    )

    @patch.object(Query.objects, 'find_by_text', return_value=qs_mock)
    def test_when_query_already_exists_raise_QueryAlreadyExistError(self, mocked):
        with pytest.raises(QueryAlreadyExistError):
            use_case = QueryRegister(
                text="query"
            )
            use_case.valid_data()

    @patch.object(Query.objects, 'find_by_text', return_value=MockSet())
    def test_when_query_does_not_exists_returns_true(self, mocked):
        expected_result = True

        use_case = QueryRegister(
            text="query"
        )
        result = use_case.valid_data()
        assert result == expected_result


class TestTweetValidData(TestCase):
    qs_mock = MockSet(
        Tweet(
            id=100,
            text='texto de prueba',
            author_id=200,
            conversation_id=300,
            created_at='01/01/2021',
            lang='es'
        )
    )

    @patch.object(Tweet.objects, 'find_by_id', return_value=qs_mock)
    def test_when_tweet_already_exists_raise_TweetAlreadyExistError(self, mocked):
        with pytest.raises(TweetAlreadyExistError):
            use_case = TweetRegister(
                _id=100,
                text='texto de prueba',
                author_id=200,
                conversation_id=300,
                created_at='01/01/2021',
                lang='es'
            )
            use_case.valid_data()

    @patch.object(Tweet.objects, 'find_by_id', return_value=MockSet())
    def test_when_tweet_does_not_exists_returns_true(self, mocked):
        expected_result = True

        use_case = TweetRegister(
            _id=100,
            text='texto de prueba',
            author_id=200,
            conversation_id=300,
            created_at='01/01/2021',
            lang='es'
        )
        result = use_case.valid_data()
        assert result == expected_result


class TestUserValidData(TestCase):
    qs_mock = MockSet(
        User(
            id=100,
            name='name',
            username='username',
            created_at='01/01/2021',
            profile_image_url='profile_image_url',
            protected=True,
            public_metrics='public_metrics',
            verified=True,
            description='description',
            location='location',
            url='url'
        )
    )

    @patch.object(User.objects, 'find_by_id', return_value=qs_mock)
    def test_when_user_already_exists_raise_UserAlreadyExistError(self, mocked):
        with pytest.raises(UserAlreadyExistError):
            use_case = UserRegister(
                _id=100,
                name='name',
                username='username',
                created_at='01/01/2021',
                profile_image_url='profile_image_url',
                protected=True,
                public_metrics='public_metrics',
                verified=True,
                description='description',
                location='location',
                url='url'
            )
            use_case.valid_data()

    @patch.object(User.objects, 'find_by_id', return_value=MockSet())
    def test_when_user_does_not_exists_returns_true(self, mocked):
        expected_result = True

        use_case = UserRegister(
            _id=100,
            name='name',
            username='username',
            created_at='01/01/2021',
            profile_image_url='profile_image_url',
            protected=True,
            public_metrics='public_metrics',
            verified=True,
            description='description',
            location='location',
            url='url',
            tweet_id=None
        )
        result = use_case.valid_data()
        assert result == expected_result


def create_query(text):
    return Query(
        text=text
    )


@patch.object(Query.objects, 'create_query', side_effect=create_query)  # we don't need to test django again
@patch.object(QueryRegister, 'valid_data', return_value=None)  # already tested on TestValidData
class TestQueryRegisterExecute(TestCase):

    def setUp(self):
        # setup method will be executed on each test
        self._use_case = QueryRegister(
            text="query"
        )

    def test_return_query_type(self, mock_create, mock_register):
        result = self._use_case.execute()
        assert isinstance(result, Query)

    def test_create_query_with_text(self, mock_create, mock_register):
        expected_result = 'query'
        query = self._use_case.execute()
        assert query.text == expected_result


def create_tweet(_id, text, author_id, conversation_id, created_at, lang):
    return Tweet(
        id=_id,
        text=text,
        author=author_id,
        conversation_id=conversation_id,
        created_at=created_at,
        lang=lang
    )


def create_user(_id, name, username, created_at, description, location, profile_image_url, protected, public_metrics,
                url, verified):
    return User(
        id=_id,
        name=name,
        username=username,
        created_at=created_at,
        description=description,
        location=location,
        profile_image_url=profile_image_url,
        protected=protected,
        public_metrics=public_metrics,
        url=url,
        verified=verified
    )


qs_user_mock = MockSet(
    User(
        id=100,
        name='name',
        username='username',
        created_at='01/01/2021',
        profile_image_url='profile_image_url',
        protected=True,
        public_metrics='public_metrics',
        verified=True,
        description='description',
        location='location',
        url='url'
    )
)


@patch.object(Tweet.objects, 'create_tweet', side_effect=create_tweet)  # we don't need to test django again
@patch.object(TweetRegister, 'valid_data', return_value=None)  # already tested on TestValidData
class TestTweetRegisterExecute(TestCase):

    def setUp(self):
        # setup method will be executed on each test
        self._use_case = TweetRegister(
            _id=100,
            text='texto de prueba',
            author_id=qs_user_mock[0],
            conversation_id=300,
            created_at='01/01/2021',
            lang='es'
        )

    def test_return_tweet_type(self, mock_create, mock_register):
        result = self._use_case.execute()
        assert isinstance(result, Tweet)

    def test_create_tweet_with_text(self, mock_create, mock_register):
        expected_result = 'texto de prueba'
        query = self._use_case.execute()
        assert query.text == expected_result


@patch.object(User.objects, 'create_user', side_effect=create_user)  # we don't need to test django again
@patch.object(UserRegister, 'valid_data', return_value=None)  # already tested on TestValidData
class TestUserRegisterExecute(TestCase):

    def setUp(self):
        # setup method will be executed on each test
        self._use_case = UserRegister(
            _id=100,
            name='name',
            username='username',
            created_at='01/01/2021',
            profile_image_url='profile_image_url',
            protected=True,
            public_metrics='public_metrics',
            verified=True,
            description='description',
            location='location',
            url='url',
            tweet_id=None
        )

    def test_return_user_type(self, mock_create, mock_register):
        result = self._use_case.execute()
        assert isinstance(result, User)

    def test_create_user_with_text(self, mock_create, mock_register):
        expected_result = 'username'
        user = self._use_case.execute()
        assert user.username == expected_result
