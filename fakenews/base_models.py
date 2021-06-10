from django.db import models
from django.urls import reverse


# FakeNews as Interface #
class FakeNewsManager(models.Manager):

    def find_by_id(self, _id):
        queryset = self.get_queryset()
        return queryset.filter(id=_id)

    def find_by_url(self, url):
        queryset = self.get_queryset()
        return queryset.filter(url=url)

    def add_post(self, fakenews, post):
        fakenews.posts.add(post)

    def get_post_queryset(self, _id):
        fakenews = self.find_by_id(_id).get()
        return fakenews.posts.all()

    def get_posts(self, _id):
        fakenews = self.find_by_id(_id).get()
        posts = []
        for post in fakenews.posts.all():
            posts.append([post.date, post.link, post.title, post.content])

        return posts


class FakeNews(models.Model):
    url = models.CharField(max_length=256, unique=True)  # max_lenght = required
    posts = models.ManyToManyField('Post', blank=True)
    objects = FakeNewsManager()
    path_detail = "fakenews:fakenews-detail"
    path_update = "fakenews:fakenews-update"
    path_delete = "fakenews:fakenews-delete"
    path_post_list = "fakenews:fakenews-post-list"
    path_post_download = "fakenews:fakenews-post-download"

    def get_absolute_url(self):
        return reverse(self.path_detail, kwargs={"pk": self.pk})

    def get_update_url(self):
        return reverse(self.path_update, kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse(self.path_delete, kwargs={"pk": self.pk})

    def get_posts_url(self):
        return reverse(self.path_post_list, kwargs={"pk": self.pk})

    def get_download_posts_url(self):
        return reverse(self.path_post_download, kwargs={"pk": self.pk})
