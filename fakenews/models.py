from django.db import models
from django.urls import reverse
from urllib.parse import urlparse
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

    def get_url_domain(self):
        return urlparse(self.url).netloc

    def get_absolute_url(self):
        return reverse("fakenews:wordpress-detail", kwargs={"pk": self.id})

    def get_update_url(self):
        return reverse("fakenews:wordpress-update", kwargs={"pk": self.id})

    def get_delete_url(self):
        return reverse("fakenews:wordpress-delete", kwargs={"pk": self.id})

    def get_posts_url(self):
        return reverse("fakenews:wordpress-post-list", kwargs={"pk": self.id})

    def get_download_posts_url(self):
        return reverse("fakenews:wordpress-post-download", kwargs={"pk": self.id})


# SOUP TYPE #
class SoupManager(FakeNewsManager):

    def create_soup(self, url, link_class, date_type, date_id):
        soup = Soup.objects.create(
            url=url,
            link_class=link_class,
            date_type=date_type,
            date_id=date_id,
        )
        soup.save()
        return soup


class Soup(FakeNews):
    ATTR_CHOICES = (
        ("1", "Id"),
        ("2", "Class")
    )
    link_class = models.CharField(max_length=120)  # max_lenght = required
    date_type = models.CharField(max_length=1, choices=ATTR_CHOICES)
    date_id = models.CharField(max_length=120)
    objects = SoupManager()

    def get_url_domain(self):
        return urlparse(self.url).netloc

    def get_absolute_url(self):
        return reverse("fakenews:soup-detail", kwargs={"pk": self.id})

    def get_update_url(self):
        return reverse("fakenews:soup-update", kwargs={"pk": self.id})

    def get_delete_url(self):
        return reverse("fakenews:soup-delete", kwargs={"pk": self.id})

    def get_posts_url(self):
        return reverse("fakenews:post-list", kwargs={"pk": self.id})

    def get_download_posts_url(self):
        return reverse("fakenews:post-download", kwargs={"pk": self.id})


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


class Post(models.Model):
    link = models.CharField(max_length=255, unique=True)
    date = models.CharField(max_length=255)
    title = models.CharField(max_length=255, default='')
    content = models.TextField()
    objects = PostManager()

    def get_absolute_url(self):
        return reverse("fakenews:wordpress-detail", kwargs={"id": self.id})
