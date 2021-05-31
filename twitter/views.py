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

from .forms import QueryCreateForm
from .models import Tweet, User, Query
from .services import (
    ResponseHandler,
    ResponseHandlerError
)


class QueryCreateView(CreateView):
    template_name = 'twitters/query-create.html'
    form_class = QueryCreateForm

    def get_success_url(self):
        return '/'

    def form_valid(self, form):
        return super().form_valid(form)

    # GET Method
    def get(self, request, *args, **kwargs):
        form = QueryCreateForm()
        context = {
            'form': form
        }
        return render(request, self.template_name, context)

    # POST Method
    def post(self, request, *args, **kwargs):
        form = QueryCreateForm(request.POST or None)

        if form.is_valid():
            # get the input and delegate to process
            self._run_handler(form)
            context = {
                'form': form
            }
            return render(request, self.template_name, context)
        else:
            context = {
                'form': form
            }
            return render(request, self.template_name, context)

    def _run_handler(self, form):
        handler = ResponseHandler(
            form.cleaned_data['query']
        )
        # handle the output
        try:
            handler.handle_response()
        except ResponseHandlerError as err:
            form.add_error('query', str(err))


class QueryUpdateView(UpdateView):
    template_name = 'twitters/query-update.html'
    form_class = QueryCreateForm
    model = Query

    def get_success_url(self):
        return '/'

    def form_valid(self, form):
        return super().form_valid(form)

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Query, id=id_)

    # GET Method
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        form = QueryCreateForm(instance=obj)
        context = {
            'object': obj,
            'form': form
        }
        return render(request, self.template_name, context)

    # POST Method
    def post(self, request, *args, **kwargs):
        obj = self.get_object()

        form = QueryCreateForm(request.POST or None, instance=obj)
        if form.is_valid():
            # get the input and delegate to process
            self._run_handler(form)
            context = {
                'form': form
            }
            return render(request, self.template_name, context)
        else:
            context = {
                'form': form
            }
            return render(request, self.template_name, context)

    def _run_handler(self, form):
        handler = ResponseHandler(
            form.cleaned_data['query']
        )
        # handle the output
        try:
            handler.handle_update_response()
        except ResponseHandlerError as err:
            form.add_error('query', str(err))


class QueryDetailView(DetailView):
    template_name = 'twitters/query-detail.html'

    def get_success_url(self):
        return '/'

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Query, id=id_)

    # GET Method
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        context = {
            'object': obj
        }
        return render(request, self.template_name, context)


class QueryDeleteView(DeleteView):
    template_name = 'twitters/query-delete.html'
    model = Query

    def get_success_url(self):
        return reverse('twitter:query-create')

    def form_valid(self, form):
        return super().form_valid(form)

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Query, id=id_)


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

    def get_object(self):
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


class TweetDownloadView(DetailView):
    template_name = 'twitters/tweet-list.html'
    error_template_name = 'twitters/twitter-error.html'

    def get_object(self):
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
            return self._run_handler(obj)
        except ResponseHandlerError as err:
            context = {
                'message': str(err)
            }
            return render(request, self.error_template_name, context)

    def _run_handler(self, obj):
        handler = ResponseHandler(
            obj.text
        )
        return handler.handle_download_response()


class TweetListView(ListView):
    template_name = 'twitters/tweet-list.html'
    paginate_by = 10  # if pagination is desired
    model = Tweet
    context_object_name = 'tweets'
    ordering = ['-id']

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Query, id=id_)

    def get_queryset(self):
        obj = self.get_object()
        handler = ResponseHandler(
            obj.text
        )
        queryset = handler.get_tweet_queryset()

        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = Query.objects.find_by_id(self.kwargs.get("id")).get()
        return context


# USERS #
class UserListView(ListView):
    template_name = 'twitters/user-list.html'
    paginate_by = 10  # if pagination is desired
    model = User
    context_object_name = 'users'
    ordering = ['-id']

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Query, id=id_)

    def get_queryset(self):
        obj = self.get_object()
        handler = ResponseHandler(
            obj.text
        )
        # get users and add to context (ahora coge tweets)
        queryset = handler.get_user_queryset()

        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = Query.objects.find_by_id(self.kwargs.get("id")).get()
        return context
