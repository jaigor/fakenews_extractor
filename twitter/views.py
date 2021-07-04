from django.shortcuts import (
    render,
    get_object_or_404
)
from django.urls import reverse
from django.http import HttpResponseRedirect

from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView
)

from .base_views import SocialListView, SocialCreateView
from .forms import QueryCreateForm
from .models import Tweet, Query
from .services import (
    ResponseHandler,
    ResponseHandlerError
)


class QueryCreateView(CreateView):

    def __init__(self, **kwargs):
        super().__init__()
        self.context = {}
        self.form_class = QueryCreateForm
        self.template_name = 'twitters/query-create.html'

    def get_success_url(self):
        return '/'

    def form_valid(self, form):
        return super().form_valid(form)

    # GET Method
    def get(self, request, *args, **kwargs):
        form = self.form_class
        self.context = {
            'form': form
        }
        return render(request, self.template_name, self.context)

    # POST Method
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST or None)

        if form.is_valid():
            # get the input and delegate to process
            self._run_handler(form)

        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def _run_handler(self, form):
        handler = ResponseHandler(
            form.cleaned_data['query']
        )
        # handle the output
        try:
            result = handler.handle_response()
            self.context['task_ids'] = [result, result.parent]

        except ResponseHandlerError as err:
            form.add_error('query', str(err))


class QueryUpdateView(UpdateView):

    def __init__(self, **kwargs):
        super().__init__()
        self.context = {}
        self.form_class = QueryCreateForm
        self.model = Query
        self.template_name = 'twitters/query-update.html'

    def get_success_url(self):
        return '/'

    def form_valid(self, form):
        return super().form_valid(form)

    # GET Method
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        form = self.form_class(instance=obj)
        self.context = {
            'object': obj,
            'form': form
        }
        return render(request, self.template_name, self.context)

    # POST Method
    def post(self, request, *args, **kwargs):
        obj = self.get_object()

        form = self.form_class(request.POST or None, instance=obj)
        if form.is_valid():
            # get the input and delegate to process
            self._run_handler(form)

        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def _run_handler(self, form):
        handler = ResponseHandler(
            form.cleaned_data['query']
        )
        # handle the output
        try:
            result = handler.handle_update_response()
            self.context['task_ids'] = [result, result.parent]

        except ResponseHandlerError as err:
            form.add_error('query', str(err))


class QueryDetailView(DetailView):
    template_name = 'twitters/query-detail.html'
    model = Query


class QueryDeleteView(DeleteView):
    template_name = 'twitters/query-delete.html'
    model = Query
    path_create = 'twitter:query-create'

    def get_success_url(self):
        return reverse(self.path_create)


class QueryListView(ListView):
    template_name = 'twitters/query-list.html'
    paginate_by = 10  # if pagination is desired
    model = Query
    context_object_name = 'querys'
    queryset = Query.objects.all()
    ordering = ['-id']


# TWEET #
class TweetCreateView(DetailView):
    template_name = 'twitters/tweet-list.html'
    error_template_name = 'twitters/twitter-error.html'

    def get_object(self, **kwargs):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Query, id=id_)

    # GET Method
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        context = {
            'object': obj
        }
        # handle the output
        try:
            # get the input and delegate to process
            self._run_handler(obj)
            return HttpResponseRedirect(reverse('twitter:tweet-list', kwargs={'id': obj.id}))
        except ResponseHandlerError as err:
            context = {
                'message': str(err)
            }
            return render(request, self.error_template_name, context)

    def _run_handler(self, obj):
        handler = ResponseHandler(
            obj.text
        )
        handler.handle_update_response()


class TweetDownloadView(SocialCreateView):
    template_name = 'twitters/tweet-list.html'
    error_template_name = 'twitters/twitter-error.html'
    response_handler = ResponseHandler
    model = Query
    exception = ResponseHandlerError


class TweetListView(SocialListView):
    template_name = 'twitters/tweet-list.html'
    model = Tweet
    context_object_name = 'tweets'
    response_handler = ResponseHandler
    parent_model = Query
    object_name = 'query'


class TweetAutoCreateView(TweetCreateView):

    def __init__(self):
        super().__init__()
        self.context = {}

    # GET Method
    def get(self, request, *args, **kwargs):
        # twitter search
        if len(self.kwargs) > 0:
            try:
                self.template_name = 'twitters/query-create.html'
                # get the input and delegate to process
                self._run_search_handler(self.kwargs['text'])
                return render(request, self.template_name, self.context)
            except ResponseHandlerError as err:
                context = {
                    'message': str(err)
                }
                return render(request, self.error_template_name, context)
        else:
            return HttpResponseRedirect(reverse('twitter:query-list'))

    def _run_search_handler(self, text):
        print(text)
        handler = ResponseHandler(
            text
        )
        # handle the output
        result = handler.handle_search_response()
        self.context['task_ids'] = [result, result.parent]