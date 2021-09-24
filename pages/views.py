from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

from .base_views import DownloadView
from .forms import ClassifierForm
from .services import (
    PostDownloadResponseHandler,
    UserDownloadResponseHandler,
    TweetDownloadResponseHandler,
    ClassifierResponseHandler
)


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


class TweetClassifierView(View):

    def __init__(self):
        super().__init__()
        self.context = {}
        self.template_name = 'classifier.html'
        self.error_template_name = 'error.html'
        self.form_class = ClassifierForm

    def get_success_url(self):
        return '/'

    # GET Method
    def get(self, request, *args, **kwargs):
        tweets = TweetDownloadResponseHandler().get_twitter_tweets_choices()
        form = self.form_class(tweets)
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    # POST Method
    def post(self, request, *args, **kwargs):
        tweets = TweetDownloadResponseHandler().get_twitter_tweets_choices()
        form = self.form_class(tweets, request.POST or None)
        self.context['form'] = form
        if form.is_valid():
            # get the input and delegate to process
            self._run_handler(form)
            return render(request, self.template_name, self.context)
        else:
            print("error")
            print(form.errors.as_data())
            return render(request, self.error_template_name, self.context)

    def _run_handler(self, form):
        handler = ClassifierResponseHandler(
            form.cleaned_data['method'],
            form.cleaned_data['tweets']
        )
        # handle the output
        try:
            results = handler.handle_classifier()
            self.context['results'] = results
            for r in results:
                print(r)

        except Exception as err:
            form.add_error('url', str(err))
