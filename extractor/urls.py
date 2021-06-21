"""extractor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from pages.views import (
    HomeView,
    AboutView,
    CsvView,
    DownloadPostsView,
    DownloadUsersView,
    DownloadTweetsView
)

urlpatterns = [
    path('twitter/', include('twitter.urls')),
    path('fakenews/', include('fakenews.urls')),

    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('csv/', CsvView.as_view(), name='csv'),
    path('downloadposts/', DownloadPostsView.as_view(), name='download-posts'),
    path('downloadusers/', DownloadUsersView.as_view(), name='download-users'),
    path('downloadtweets/', DownloadTweetsView.as_view(), name='download-tweets'),
    path('celery-progress/', include('celery_progress.urls')),
    path('admin/', admin.site.urls),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)