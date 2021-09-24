from django.db import models
from django.urls import reverse
from django.utils import dateparse


class UserManager(models.Manager):

    def find_by_id(self, _id):
        queryset = self.get_queryset()
        return queryset.filter(user_id=_id)

    def add_tweet(self, user, tweet):
        user.tweets.add(tweet)

    def get_all_users(self):
        users = []
        for user in User.objects.all():
            tweets_ids = []
            for tweet in user.tweets.all():
                tweets_ids.append(tweet.tweet_id)

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
                user.verified,
                tweets_ids
            ])
        return users

    def create_user(self, _id, name, username, created_at, description, location, profile_image_url, protected,
                    public_metrics, url, verified):
        user = User.objects.create(
            user_id=_id,
            name=name,
            username=username,
            created_at=created_at,
            description=description,
            location=location,
            profile_image_url=profile_image_url,
            protected=protected,
            public_metrics=public_metrics,
            url=url,
            verified=verified)
        user.save()
        return user

    def update_user(self, _id, name, username, created_at, description, location, profile_image_url, protected,
                    public_metrics, url, verified):
        return User.objects.find_by_id(_id).update(
            user_id=_id,
            name=name,
            username=username,
            created_at=created_at,
            description=description,
            location=location,
            profile_image_url=profile_image_url,
            protected=protected,
            public_metrics=public_metrics,
            url=url,
            verified=verified)


class User(models.Model):
    user_id = models.CharField(max_length=120, unique=True, null=True)
    name = models.CharField(max_length=120)
    username = models.CharField(max_length=120)
    created_at = models.TextField()
    description = models.TextField(null=True)
    location = models.TextField(null=True)
    profile_image_url = models.TextField()
    protected = models.BooleanField()
    public_metrics = models.TextField()
    url = models.TextField()
    verified = models.BooleanField()
    tweets = models.ManyToManyField('Tweet', blank=True)
    objects = UserManager()

    def get_absolute_url(self):
        return reverse("twitter:user-detail", kwargs={"id": self.pk})

    def get_formatted_date(self):
        return dateparse.parse_datetime(self.created_at)

    def __str__(self):
        return "%s - %s" % (self.username, self.name)


class TweetManager(models.Manager):

    def find_by_id(self, _id):
        queryset = self.get_queryset()
        return queryset.filter(tweet_id=_id)

    def create_tweet(self, _id, text, author, conversation_id, created_at, lang):
        tweet = Tweet.objects.create(
            tweet_id=_id,
            text=text,
            author=author,
            conversation_id=conversation_id,
            created_at=created_at,
            lang=lang)
        tweet.save()
        return tweet

    def update_tweet(self, _id, text, author, conversation_id, created_at, lang):
        return Tweet.objects.find_by_id(_id).update(
            tweet_id=_id,
            text=text,
            author=author,
            conversation_id=conversation_id,
            created_at=created_at,
            lang=lang)

    def update_spreader(self, _id, _percentage):
        tweet = Tweet.objects.find_by_id(_id).get()
        # spreader > 0.78
        spreader = False

        if _percentage > 0.78:
            spreader = True

        Tweet.objects.find_by_id(_id).update(
            tweet_id=_id,
            text=tweet.text,
            author=tweet.author,
            conversation_id=tweet.conversation_id,
            created_at=tweet.created_at,
            lang=tweet.lang,
            spreader=spreader,
            percentage=_percentage)

        return Tweet.objects.find_by_id(_id).get()

    def get_all_tweets(self):
        tweets = []
        for tweet in Tweet.objects.all():
            tweets.append([
                tweet.text,
                tweet.author.name,
                tweet.conversation_id,
                tweet.created_at,
                tweet.lang,
                tweet.spreader,
                tweet.percentage
            ])
        return tweets

    def get_all_tweets_choices(self):
        tweets = ()
        for tweet in Tweet.objects.all():
            tweets = tweets + ((tweet.tweet_id, tweet.text),)

        return tweets


class Tweet(models.Model):

    tweet_id = models.CharField(max_length=120, unique=True, null=True)  # max_lenght = required
    text = models.TextField()
    author = models.OneToOneField('User', on_delete=models.CASCADE)
    conversation_id = models.TextField()
    created_at = models.TextField()
    lang = models.CharField(null=True, max_length=5)
    spreader = models.BooleanField(null=True, default=False)
    percentage = models.FloatField(null=True, default=0.0)
    objects = TweetManager()

    def get_absolute_url(self):
        return reverse("twitter:tweet-detail", kwargs={"id": self.pk})

    def get_formatted_date(self):
        return dateparse.parse_datetime(self.created_at)

    def __str__(self):
        return "%s - %s" % (self.created_at, self.text)


class QueryManager(models.Manager):

    def find_by_id(self, _id):
        queryset = self.get_queryset()
        return queryset.filter(id=_id)

    def find_by_text(self, text):
        queryset = self.get_queryset()
        return queryset.filter(text=text)

    def get_tweet_queryset(self, _id):
        query = self.find_by_id(_id).get()
        return query.tweets.all()

    def add_tweet(self, query, tweet):
        query.tweets.add(tweet)

    def get_tweets(self, _id):
        query = self.find_by_id(_id).get()
        tweets = []
        for tweet in query.tweets.all():
            tweets.append([tweet.text, tweet.author, tweet.conversation_id, tweet.created_at, tweet.lang])
        return tweets

    def create_query(self, text):
        query = Query.objects.create(
            text=text,
        )
        query.save()
        return query

    def update_query(self, text):
        return Query.objects.find_by_text(text).update(
            text=text
        )


class Query(models.Model):
    text = models.CharField(max_length=512, unique=True)  # max_lenght = required
    tweets = models.ManyToManyField('Tweet', blank=True)  # can be null = Empty
    objects = QueryManager()
    path_detail = "twitter:query-detail"
    path_update = "twitter:query-update"
    path_delete = "twitter:query-delete"
    path_tweet_list = "twitter:tweet-list"
    path_tweet_download = "twitter:tweet-download"

    def get_absolute_url(self):
        return reverse(self.path_detail, kwargs={"pk": self.pk})

    def get_update_url(self):
        return reverse(self.path_update, kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse(self.path_delete, kwargs={"pk": self.pk})

    def get_tweets_url(self):
        return reverse(self.path_tweet_list, kwargs={"pk": self.pk})

    def get_download_tweets_url(self):
        return reverse(self.path_tweet_download, kwargs={"pk": self.pk})

    def get_update_tweets_url(self):
        return reverse("twitter:tweet-update", kwargs={"pk": self.pk})

    def get_users_url(self):
        return reverse("twitter:user-list", kwargs={"pk": self.pk})

    #def __str__(self):
    #    return self.text
