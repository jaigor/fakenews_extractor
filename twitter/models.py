from django.db import models
from django.urls import reverse
from django.utils import dateparse
from urllib.parse import urlparse

class UserManager(models.Manager):
    
    def find_by_id(self, id):
        queryset = self.get_queryset()
        return queryset.filter(id=id)

    def add_tweet(self, id, tweet):
        user = self.find_by_id(id).get()
        user.tweets.add(tweet)

    def get_all_users(self):
        users = []
        for user in User.objects.all():
            users.append([
                user.name,
                user.username, 
                user.created_at, 
                user.description, 
                user.location, 
                user.profile_image_url,
                user.protected,
                user.public_metrics,
                user.url,
                user.verified
                ])

        return users

class User(models.Model):
    id                  = models.CharField(primary_key=True, max_length=120, unique=True)
    name                = models.CharField(max_length=120)
    username            = models.CharField(max_length=120)
    created_at          = models.TextField()
    description         = models.TextField(null=True)
    location            = models.TextField(null=True)
    profile_image_url   = models.TextField()
    protected           = models.BooleanField()
    public_metrics      = models.TextField()
    url                 = models.TextField()
    verified            = models.BooleanField()
    tweets              = models.ManyToManyField('Tweet', blank=True)
    objects             = UserManager()

    def get_absolute_url(self):
        return reverse("twitter:user-detail", kwargs={"id": self.id})

    def get_formatted_date(self):
        return dateparse.parse_datetime(created_at)

    def __str__(self):
        return "%s - %s" % (self.username, self.name)

class TweetManager(models.Manager):
    
    def find_by_id(self, id):
        queryset = self.get_queryset()
        return queryset.filter(id=id)

    def add_author(self, id, user):
        tweet = self.find_by_id(id)
        tweet.author = user

class Tweet(models.Model):
    id                  = models.CharField(primary_key=True, max_length=120, unique=True) #max_lenght = required
    text                = models.TextField()
    author              = models.ForeignKey(User, null=True, on_delete=models.CASCADE,  blank=True)
    conversation_id     = models.TextField()
    created_at          = models.TextField()
    lang                = models.CharField(null=True, max_length=5)
    objects             = TweetManager()

    def get_absolute_url(self):
        return reverse("twitter:tweet-detail", kwargs={"id": self.id})

    def get_formatted_date(self):
        return dateparse.parse_datetime(created_at)

    def __str__(self):
        return "%s - %s" % (self.created_at, self.text)

class QueryManager(models.Manager):
    
    def find_by_id(self, id):
        queryset = self.get_queryset()
        return queryset.filter(id=id)

    def find_by_text(self, text):
        queryset = self.get_queryset()
        return queryset.filter(text=text)

    def get_tweet_queryset(self, id):
        query = self.find_by_id(id).get()
        return query.tweets.all()
    
    def add_tweet(self, text, tweet):
        query = self.find_by_text(text).get()
        query.tweets.add(tweet)

    def get_tweets(self, id):
        query = self.find_by_id(id).get()
        tweets = []
        for tweet in query.tweets.all():
            tweets.append([tweet.text, tweet.author, tweet.conversation_id, tweet.created_at, tweet.lang])

        return tweets

class Query(models.Model):
    text                = models.CharField(max_length=256, unique=True) #max_lenght = required
    tweets              = models.ManyToManyField(Tweet, blank=True)  # can be null = Empty
    objects             = QueryManager()

    def get_absolute_url(self):
        return reverse("twitter:query-detail", kwargs={"id": self.id})

    def get_formatted_date(self):
        return dateparse.parse_datetime(created_at)
    
    def get_tweets_url(self):
        return reverse("twitter:tweet-list", kwargs={"id": self.id})     

    def get_update_tweets_url(self):
        return reverse("twitter:tweet-update", kwargs={"id": self.id})

    def get_download_tweets_url(self):
        return reverse("twitter:tweet-download", kwargs={"id": self.id})

    def get_users_url(self):
        return reverse("twitter:user-list", kwargs={"id": self.id})

    def __str__(self):
        return self.text