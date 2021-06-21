from django.views.generic import TemplateView

from .base_views import DownloadView
from .services import (
    PostDownloadResponseHandler,
    UserDownloadResponseHandler,
    TweetDownloadResponseHandler
)


# Create your views here.
class HomeView(TemplateView):
    template_name = 'home.html'


class AboutView(TemplateView):
    template_name = 'about.html'


class CsvView(TemplateView):
    template_name = 'download.html'


class DownloadPostsView(DownloadView):
    template_name = 'download.html'
    error_template_name = 'error.html'

    def _run_handler(self):
        handler = PostDownloadResponseHandler()
        return handler.handle_all_response()


class DownloadUsersView(DownloadView):
    template_name = 'download.html'
    error_template_name = 'error.html'

    def _run_handler(self):
        handler = UserDownloadResponseHandler()
        return handler.handle_all_response()


class DownloadTweetsView(DownloadView):
    template_name = 'download.html'
    error_template_name = 'error.html'

    def _run_handler(self):
        handler = TweetDownloadResponseHandler()
        return handler.handle_all_response()
