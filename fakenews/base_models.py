from django.db import models


# FakeNews as Interface #
class FakeNewsManager(models.Manager):

    def find_by_id(self, id):
        queryset = self.get_queryset()
        return queryset.filter(id=id)

    def find_by_url(self, url):
        queryset = self.get_queryset()
        return queryset.filter(url=url)

    def add_post(self, fakenews, post):
        fakenews.posts.add(post)

    def get_post_queryset(self, id):
        fakenews = self.find_by_id(id).get()
        return fakenews.posts.all()

    def get_posts(self, id):
        fakenews = self.find_by_id(id).get()
        posts = []
        for post in fakenews.posts.all():
            posts.append([post.date, post.link, post.title, post.content])

        return posts


class FakeNews(models.Model):
    url = models.CharField(max_length=256, unique=True)  # max_lenght = required
    posts = models.ManyToManyField('Post', blank=True)
    objects = FakeNewsManager()
