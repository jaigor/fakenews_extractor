from django.shortcuts import render
from django.views.generic import TemplateView
from pages.base_services import ResponseHandlerError


class DownloadView(TemplateView):
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
        pass