from django.urls import path

from soup.views import (
    SoupCreateView,
    SoupDetailView,
    SoupUpdateView,
    SoupDeleteView,
    SoupListView,
    PostCreateView,
    PostListView,
    PostDownloadView
)

app_name = 'soup'
urlpatterns = [
    path('', SoupListView.as_view(), name='soup-list'),
    path('list/', SoupListView.as_view(), name='soup-list'),
    path('create/', SoupCreateView.as_view(), name='soup-create'),
    path('<int:id>/', SoupDetailView.as_view(), name='soup-detail'),
    path('<int:id>/update/', SoupUpdateView.as_view(), name='soup-update'),
    path('<int:id>/delete/', SoupDeleteView.as_view(), name='soup-delete'),    
    
    path('<int:id>/createposts/', PostCreateView.as_view(), name='post-create'),
    path('<int:id>/updateposts/', PostCreateView.as_view(), name='post-update'),
    path('<int:id>/download/', PostDownloadView.as_view(), name='post-download'),
    path('<int:id>/listpost/', PostListView.as_view(), name='post-list'),
]