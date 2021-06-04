from django_mock_queries.query import MockSet
from django.test import TestCase
from mock import patch

from wordpress.models import Wordpress, Post


class TestModelsManager(TestCase):
    post_object = [
        Post(
            link="www.wordpress.com/posts/1",
            date="01/01/2021",
            title="Post",
            content="Post Content"
        )
    ]
    qs_post_mock = MockSet(post_object[0])
    wordpress_object = [
        Wordpress(
            id=100,
            url="www.wordpress.com/data",
            post_type="Pages",
            domain="www.wordpress.com"
        )
    ]
    qs_wordpress_mock = MockSet(wordpress_object[0])

    @patch.object(Wordpress.objects, 'get_queryset', return_value=qs_wordpress_mock)
    def test_wordpress_is_created_and_returned_by_id(self, mocked):
        result = list(Wordpress.objects.find_by_id(100))
        assert result == self.wordpress_object

    @patch.object(Wordpress.objects, 'get_queryset', return_value=qs_wordpress_mock)
    def test_wordpress_is_created_and_returned_by_url(self, mocked):
        result = list(Wordpress.objects.find_by_url('www.wordpress.com/data'))
        assert result == self.wordpress_object

    @patch.object(Wordpress.objects, 'get_queryset', return_value=qs_wordpress_mock)
    def test_wordpress_is_created_and_returned_by_domain(self, mocked):
        result = list(Wordpress.objects.find_by_domain('www.wordpress.com'))
        assert result == self.wordpress_object

    def test_wordpress_is_created(self):
        result = self._generate_wordpress()
        assert result == self.wordpress_object[0]

    def test_wordpress_update_result(self):
        wordpress = self._generate_wordpress()
        Wordpress.objects.update_wordpress(url=wordpress.url, post_type="test", domain=wordpress.domain)
        wordpress = Wordpress.objects.find_by_url(wordpress.url).get()

        self.assertEqual(wordpress.post_type, "test")

    def test_add_post_and_count_them(self):
        wordpress = self._generate_wordpress()
        posts_before = len(wordpress.posts.all())

        post = self._generate_post()
        Wordpress.objects.add_post(wordpress, post)
        posts_now = len(wordpress.posts.all())

        assert posts_now == posts_before + 1

    @patch.object(Wordpress.objects, 'get_queryset', return_value=qs_wordpress_mock)
    def test_post_queryset_is_returned(self, mocked):
        wordpress = self._generate_wordpress()
        post = self._generate_post()
        wordpress.posts.add(post)

        result_qs = Wordpress.objects.get_post_queryset(100)
        result = result_qs.get()

        assert result == self.post_object[0]

    @patch.object(Wordpress.objects, 'get_queryset', return_value=qs_wordpress_mock)
    def test_post_array_is_returned_and_compared_link(self, mocked):
        wordpress = self._generate_wordpress()
        post = self._generate_post()
        wordpress.posts.add(post)

        result_array = Wordpress.objects.get_posts(100)

        assert result_array[0][1] == self.post_object[0].link

    @patch.object(Post.objects, 'get_queryset', return_value=qs_post_mock)
    def test_post_is_created_and_returned_by_link(self, mocked):
        result = list(Post.objects.find_by_link("www.wordpress.com/posts/1"))
        assert result == self.post_object

    def test_post_is_created(self):
        result = self._generate_post()
        assert result == self.post_object[0]

    def test_post_update_result(self):
        post = self._generate_post()
        Post.objects.update_post(date="test", link=post.link, title=post.title, content=post.content)
        post = Post.objects.find_by_link(post.link).get()

        self.assertEqual(post.date, "test")

    @patch.object(Wordpress.objects, 'create', return_value=wordpress_object[0])
    def _generate_wordpress(self, mocked):
        return Wordpress.objects.create_wordpress(
            url="www.wordpress.com/data",
            post_type="Pages",
            domain="www.wordpress.com"
        )

    @patch.object(Post.objects, 'create', return_value=post_object[0])
    def _generate_post(self, mocked):
        return Post.objects.create_post(
            link="www.wordpress.com/posts/1",
            date="01/01/2021",
            title="Post",
            content="Post Content"
        )
