from django.urls import path

from wordpress.views import (
    WordpressCreateView,
    WordpressDetailView,
    WordpressUpdateView,
    WordpressDeleteView,
    WordpressListView,
    PostCreateView,
    PostDownloadView,
    PostListView
)

app_name = 'wordpress'
urlpatterns = [
    path('', WordpressListView.as_view(), name='wordpress-list'),
    path('list/', WordpressListView.as_view(), name='wordpress-list'),
    path('create/', WordpressCreateView.as_view(), name='wordpress-create'),
    path('<int:id>/', WordpressDetailView.as_view(), name='wordpress-detail'),
    path('<int:id>/update/', WordpressUpdateView.as_view(), name='wordpress-update'),
    path('<int:id>/delete/', WordpressDeleteView.as_view(), name='wordpress-delete'),

    path('<int:id>/createposts/', PostCreateView.as_view(), name='post-create'),
    path('<int:id>/updateposts/', PostCreateView.as_view(), name='post-update'),
    path('<int:id>/downloadposts/', PostDownloadView.as_view(), name='post-download'),
    path('<int:id>/listpost/', PostListView.as_view(), name='post-list'),
]