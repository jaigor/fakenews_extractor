from django.urls import path

from twitter.views import (
    QueryCreateView,
    QueryDetailView,
    QueryUpdateView,
    QueryDeleteView,
    QueryListView,
    TweetCreateView,
    TweetDownloadView,
    TweetListView,
    UserListView
)

app_name = 'twitter'
urlpatterns = [
    path('', QueryListView.as_view(), name='query-list'),
    path('list/', QueryListView.as_view(), name='query-list'),
    path('create/', QueryCreateView.as_view(), name='query-create'),
    path('<int:id>/', QueryDetailView.as_view(), name='query-detail'),
    path('<int:id>/update/', QueryUpdateView.as_view(), name='query-update'),
    path('<int:id>/delete/', QueryDeleteView.as_view(), name='query-delete'),
    
    path('<int:id>/createtweets/', TweetCreateView.as_view(), name='tweet-create'),
    path('<int:id>/updatetweets/', TweetCreateView.as_view(), name='tweet-update'),
    path('<int:id>/downloadtweets/', TweetDownloadView.as_view(), name='tweet-download'),
    path('<int:id>/listtweet/', TweetListView.as_view(), name='tweet-list'),

    path('<int:id>/listuser/', UserListView.as_view(), name='user-list'),
]