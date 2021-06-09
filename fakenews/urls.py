from django.urls import path

from .views import (
    IndexView,

    WordpressCreateView,
    WordpressDetailView,
    WordpressUpdateView,
    WordpressDeleteView,
    WordpressListView,
    WordpressPostDownloadView,
    WordpressPostListView,

    SoupCreateView,
    SoupUpdateView,
    SoupDetailView,
    SoupDeleteView,
    SoupListView,
    SoupPostDownloadView,
    SoupPostListView,
)

app_name = 'fakenews'
urlpatterns = [
    # make index
    path('', IndexView.as_view(), name='index'),

    path('wordpress/', WordpressListView.as_view(), name='wordpress-list'),
    path('wordpress/list/', WordpressListView.as_view(), name='wordpress-list'),
    path('wordpress/create/', WordpressCreateView.as_view(), name='wordpress-create'),
    path('wordpress/<int:pk>/', WordpressDetailView.as_view(), name='wordpress-detail'),
    path('wordpress/<int:pk>/update/', WordpressUpdateView.as_view(), name='wordpress-update'),
    path('wordpress/<int:pk>/delete/', WordpressDeleteView.as_view(), name='wordpress-delete'),
    path('wordpress/<int:pk>/downloadposts/', WordpressPostDownloadView.as_view(), name='wordpress-post-download'),
    path('wordpress/<int:pk>/listpost/', WordpressPostListView.as_view(), name='wordpress-post-list'),

    path('soup/', SoupListView.as_view(), name='soup-list'),
    path('soup/list/', SoupListView.as_view(), name='soup-list'),
    path('soup/create/', SoupCreateView.as_view(), name='soup-create'),
    path('soup/<int:pk>/', SoupDetailView.as_view(), name='soup-detail'),
    path('soup/<int:pk>/update/', SoupUpdateView.as_view(), name='soup-update'),
    path('soup/<int:pk>/delete/', SoupDeleteView.as_view(), name='soup-delete'),
    path('soup/<int:pk>/updateposts/', SoupPostDownloadView.as_view(), name='soup-post-download'),
    path('soup/<int:pk>/listpost/', SoupPostListView.as_view(), name='soup-post-list'),

]
