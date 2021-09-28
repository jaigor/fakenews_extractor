from django.urls import path

from twitter.views import (
    QueryCreateView,
    QueryDetailView,
    QueryUpdateView,
    QueryDeleteView,
    QueryListView,
    TweetCreateView,
    TweetUpdateView,
    TweetDetailView,
    TweetDeleteView,
    TweetDownloadView,
    TweetListView,
    TweetAutoCreateView
)

app_name = 'twitter'
urlpatterns = [
    path('', QueryListView.as_view(), name='query-list'),
    path('list/', QueryListView.as_view(), name='query-list'),
    path('create/', QueryCreateView.as_view(), name='query-create'),
    path('<int:pk>/', QueryDetailView.as_view(), name='query-detail'),
    path('<int:pk>/update/', QueryUpdateView.as_view(), name='query-update'),
    path('<int:pk>/delete/', QueryDeleteView.as_view(), name='query-delete'),

    path('<int:pk>/createtweets/', TweetCreateView.as_view(), name='tweet-create'),
    path('<int:pk>/updatetweets/', TweetUpdateView.as_view(), name='tweet-update'),
    path('<int:pk>/detailtweets/', TweetDetailView.as_view(), name='tweet-detail'),
    path('<int:pk>/deletetweets/', TweetDeleteView.as_view(), name='tweet-delete'),
    path('<int:pk>/downloadtweets/', TweetDownloadView.as_view(), name='tweet-download'),
    path('<int:pk>/listtweet/', TweetListView.as_view(), name='tweet-list'),
    path('create/<int:pk>', TweetAutoCreateView.as_view(), name='tweet-create-text'),
]
