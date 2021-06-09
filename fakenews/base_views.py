from django.shortcuts import (
    render
)
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView
)

from .base_services import ResponseHandlerError
from .forms import (
    FakeNewsForm
)
from .models import (
    FakeNews,
    Post
)


# Interfaces #
class FakeNewsCreateView(CreateView):

    def __init__(self, **kwargs):
        super().__init__()
        self.context = {}
        self.form_class = FakeNewsForm

    def get_success_url(self):
        return '/'

    def form_valid(self, form):
        return super().form_valid(form)

    # GET Method
    def get(self, request, *args, **kwargs):
        form = self.form_class()
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
        pass


class FakeNewsUpdateView(UpdateView):

    def __init__(self, **kwargs):
        super().__init__()
        self.context = {}
        self.form_class = FakeNewsForm
        self.model = FakeNews

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
        pass


class FakeNewsDetailView(DetailView):
    model = FakeNews


class FakeNewsDeleteView(DeleteView):
    model = FakeNews
    pattern = 'fakenews:fakenews-create'

    def get_success_url(self):
        return reverse(self.pattern)


class FakeNewsListView(ListView):
    paginate_by = 10  # if pagination is desired
    model = FakeNews
    queryset = FakeNews.objects.all()
    ordering = ['-id']


# POST #

class PostCreateView(DetailView):

    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.response_handler = None
        self.error_template_name = None

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        # handle the output
        return self._run_handler(request, obj)

    def _run_handler(self, request, obj):
        try:
            # get the input and delegate to process
            handler = self.response_handler(
                obj.url
            )
            return handler.handle_download_response()
        except ResponseHandlerError as err:
            context = {
                'message': str(err)
            }
            return render(request, self.error_template_name, context)


class PostListView(ListView):
    paginate_by = 10  # if pagination is desired
    model = Post
    context_object_name = 'posts'
    ordering = ['-id']
    response_handler = None
    parent_model = FakeNews

    def get_queryset(self):
        handler = self.response_handler()
        queryset = handler.get_queryset(self.kwargs.get("pk"))

        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fakenews'] = self.parent_model.objects.find_by_id(self.kwargs.get("pk")).get()
        return context
