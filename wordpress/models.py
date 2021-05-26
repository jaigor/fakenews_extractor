from django.db import models
from django.urls import reverse
from urllib.parse import urlparse

class WordpressManager(models.Manager):
    
    def find_by_id(self, id):
        queryset = self.get_queryset()
        return queryset.filter(id=id)

    def find_by_url(self, url):
        queryset = self.get_queryset()
        return queryset.filter(url=url)
    
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

    def add_post(self, wordpress, post):
        wordpress.posts.add(post)

    def get_post_queryset(self, id):
        wordpress = self.find_by_id(id).get()
        return wordpress.posts.all()

    def get_posts(self, id):
        wordpress = self.find_by_id(id).get()
        posts = []
        for post in wordpress.posts.all():
            posts.append([post.date, post.link, post.title, post.content])

        return posts

class Wordpress(models.Model):
    url         = models.CharField(max_length=120, unique=True) #max_lenght = required
    post_type   = models.CharField(max_length=120, default='')
    domain      = models.CharField(max_length=120, default='')
    posts       = models.ManyToManyField('Post', blank=True)
    objects     = WordpressManager()

    def get_url_domain(self):
        return urlparse(self.url).netloc

    def get_absolute_url(self):
        return reverse("wordpress:wordpress-detail", kwargs={"id": self.id})

    def get_update_url(self):
        return reverse("wordpress:wordpress-update", kwargs={"id": self.id})

    def get_delete_url(self):
        return reverse("wordpress:wordpress-delete", kwargs={"id": self.id})

    def get_posts_url(self):
        return reverse("wordpress:post-list", kwargs={"id": self.id})

    def get_update_posts_url(self):
        return reverse("wordpress:post-update", kwargs={"id": self.id})

    def get_download_posts_url(self):
        return reverse("wordpress:post-download", kwargs={"id": self.id})

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
    link        = models.CharField(max_length=120, unique=True)
    date        = models.CharField(max_length=120) #max_lenght = required
    title       = models.CharField(max_length=120, default='')
    content     = models.TextField()
    objects     = PostManager()

    def get_absolute_url(self):
        return reverse("wordpress:wordpress-detail", kwargs={"id": self.id})
