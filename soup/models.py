from django.db import models
from django.urls import reverse
from urllib.parse import urlparse

class SoupManager(models.Manager):

    def find_by_id(self, id):
        queryset = self.get_queryset()
        return queryset.filter(id=id)
    
    def find_by_url(self, url):
        queryset = self.get_queryset()
        return queryset.filter(url=url)

    def create_soup(self, url, link_class, date_type, date_id):
        soup = Soup.objects.create(
            url=url,
            link_class=link_class,
            date_type=date_type,
            date_id=date_id,
            )
        soup.save()
        return soup
    
    def add_post(self, soup, post):
        soup.posts.add(post)

    def get_post_queryset(self, id):
        soup = self.find_by_id(id).get()
        return soup.posts.all()

    def get_posts(self, id):
        soup = self.find_by_id(id).get()
        posts = []
        for post in soup.posts.all():
            posts.append([post.date, post.link, post.title, post.content])

        return posts

class Soup(models.Model):

    ATTR_CHOICES =( 
        ("1", "Id"),
        ("2", "Class")
    )
    url         = models.CharField(max_length=120, unique=True) #max_lenght = required
    link_class  = models.CharField(max_length=120) #max_lenght = required
    date_type   = models.CharField(max_length=1, choices=ATTR_CHOICES)
    date_id     = models.CharField(max_length=120)
    posts       = models.ManyToManyField('Post', blank=True)
    objects     = SoupManager()

    def get_url_domain(self):
        return urlparse(self.url).netloc

    def get_absolute_url(self):
        return reverse("soup:soup-detail", kwargs={"id": self.id})   

    def get_update_url(self):
        return reverse("soup:soup-update", kwargs={"id": self.id})

    def get_delete_url(self):
        return reverse("soup:soup-delete", kwargs={"id": self.id})

    def get_posts_url(self):
        return reverse("soup:post-list", kwargs={"id": self.id})

    def get_update_posts_url(self):
        return reverse("soup:post-update", kwargs={"id": self.id})

    def get_download_posts_url(self):
        return reverse("soup:post-download", kwargs={"id": self.id})


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

    def get_all_posts(self):
        posts = []
        for post in Post.objects.all():
            posts.append([post.date, post.link, post.title, post.content])

        return posts

class Post(models.Model):
    link        = models.CharField(max_length=120, unique=True)
    date        = models.CharField(max_length=120) #max_lenght = required
    title       = models.CharField(max_length=120, default='')
    content     = models.TextField()
    objects     = PostManager()

    def get_absolute_url(self):
        return reverse("wordpress:wordpress-detail", kwargs={"id": self.id})
