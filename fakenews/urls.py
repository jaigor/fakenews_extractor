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
    SoupPostCreateView,
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
    path('wordpress/<int:id>/', WordpressDetailView.as_view(), name='wordpress-detail'),
    path('wordpress/<int:id>/update/', WordpressUpdateView.as_view(), name='wordpress-update'),
    path('wordpress/<int:id>/delete/', WordpressDeleteView.as_view(), name='wordpress-delete'),
    path('wordpress/<int:id>/downloadposts/', WordpressPostDownloadView.as_view(), name='wordpress-post-download'),
    path('wordpress/<int:id>/listpost/', WordpressPostListView.as_view(), name='wordpress-post-list'),

    path('soup/', SoupListView.as_view(), name='soup-list'),
    path('soup/list/', SoupListView.as_view(), name='soup-list'),
    path('soup/create/', SoupCreateView.as_view(), name='soup-create'),
    path('soup/<int:id>/', SoupDetailView.as_view(), name='soup-detail'),
    path('soup/<int:id>/update/', SoupUpdateView.as_view(), name='soup-update'),
    path('soup/<int:id>/delete/', SoupDeleteView.as_view(), name='soup-delete'),
    path('soup/<int:id>/createposts/', SoupPostCreateView.as_view(), name='soup-post-create'),
    path('soup/<int:id>/updateposts/', SoupPostDownloadView.as_view(), name='soup-post-update'),
    path('soup/<int:id>/listpost/', SoupPostListView.as_view(), name='soup-post-list'),

    
]