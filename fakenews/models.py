from django.db import models
from .base_models import FakeNewsManager, FakeNews


# Wordpress type #
class WordpressManager(FakeNewsManager):

    def find_by_domain(self, domain):
        queryset = self.get_queryset()
        return queryset.filter(domain=domain)

    def create_wordpress(self, url, post_type, domain):
        wordpress = Wordpress.objects.create(
            url=url,
            post_type=post_type,
            domain=domain,
        )
        wordpress.save()
        return wordpress

    def update_wordpress(self, url, post_type, domain):
        return Wordpress.objects.find_by_url(url).update(
            url=url,
            post_type=post_type,
            domain=domain,
        )


class Wordpress(FakeNews):
    post_type = models.CharField(max_length=120, default='')
    domain = models.CharField(max_length=120, default='')
    objects = WordpressManager()
    path_detail = "fakenews:wordpress-detail"
    path_update = "fakenews:wordpress-update"
    path_delete = "fakenews:wordpress-delete"
    path_post_list = "fakenews:wordpress-post-list"
    path_post_download = "fakenews:wordpress-post-download"


# SOUP TYPE #
class SoupManager(FakeNewsManager):

    def create_soup(self, url, link_class, date_type, date_id, body_class=None):
        soup = Soup.objects.create(
            url=url,
            link_class=link_class,
            date_type=date_type,
            date_id=date_id,
            body_class=body_class
        )
        soup.save()
        return soup

    def update_soup(self, url, link_class, date_type, date_id, body_class=None):
        return Soup.objects.find_by_url(url).update(
            url=url,
            link_class=link_class,
            date_type=date_type,
            date_id=date_id,
            body_class=body_class
        )


class Soup(FakeNews):
    ATTR_CHOICES = (
        ("1", "Id"),
        ("2", "Class")
    )
    link_class = models.CharField(max_length=120)  # max_lenght = required
    date_type = models.CharField(max_length=1, choices=ATTR_CHOICES)
    date_id = models.CharField(max_length=120)
    body_class = models.CharField(max_length=120, null=True, blank=True)
    objects = SoupManager()
    path_detail = "fakenews:soup-detail"
    path_update = "fakenews:soup-update"
    path_delete = "fakenews:soup-delete"
    path_post_list = "fakenews:soup-post-list"
    path_post_download = "fakenews:soup-post-download"


# POSTS #
class PostManager(models.Manager):

    def find_by_link(self, link):
        queryset = self.get_queryset()
        return queryset.filter(link=link)

    def create_post(self, date, link, title, content):
        post = Post.objects.create(
            date=date,
            link=link,
            title=title,
            content=content,
        )
        post.save()
        return post

    def update_post(self, date, link, title, content):
        return Post.objects.find_by_link(link).update(
            date=date,
            link=link,
            title=title,
            content=content,
        )

    def get_all_posts(self):
        posts = []
        for post in Post.objects.all():
            posts.append([
                post.date,
                post.link,
                post.title,
                post.content])

        return posts

    def get_all_posts_titles(self):
        titles = []
        for post in Post.objects.all():
            titles.append(post.title)

        return titles


class Post(models.Model):
    link = models.CharField(max_length=256, unique=True)
    date = models.CharField(max_length=256)
    title = models.CharField(max_length=256, default='')
    content = models.TextField()
    objects = PostManager()

    def __str__(self):
        return "%s - %s" % (self.pk, self.title)
