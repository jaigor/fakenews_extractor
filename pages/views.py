from django.views.generic import TemplateView
from django.shortcuts import (
    render
)

from .services import (
    DownloadResponseHandler,
    ResponseHandlerError
)


# Create your views here.
class HomeView(TemplateView):
    template_name = 'home.html'


class AboutView(TemplateView):
    template_name = 'about.html'


class CsvView(TemplateView):
    template_name = 'download.html'


class DownloadPostsView(TemplateView):
    template_name = 'download.html'
    error_template_name = 'error.html'

    # GET Method
    def get(self, request, *args, **kwargs):
        # handle the output
        try:
            # get the input and delegate to process
            return self._run_handler()
        except ResponseHandlerError as err:
            context = {
                'message': str(err)
            }
            return render(request, self.error_template_name, context)

    def _run_handler(self):
        handler = DownloadResponseHandler(
        )
        return handler.handle_all_posts_response()


class DownloadUsersView(TemplateView):
    template_name = 'download.html'
    error_template_name = 'error.html'

    # GET Method
    def get(self, request, *args, **kwargs):
        # handle the output
        try:
            # get the input and delegate to process
            return self._run_handler()
        except ResponseHandlerError as err:
            context = {
                'message': str(err)
            }
            return render(request, self.error_template_name, context)

    def _run_handler(self):
        handler = DownloadResponseHandler(
        )
        return handler.handle_all_users_response()
