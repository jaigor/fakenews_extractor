from django.views.generic.base import TemplateView

from .base_views import (
    FakeNewsCreateView,
    FakeNewsUpdateView,
    FakeNewsDetailView,
    FakeNewsDeleteView,
    FakeNewsListView,
    PostCreateView,
    PostListView
)

from .forms import (
    WordpressCreateForm,
    WordpressUpdateForm,
    SoupCreateForm
)
from .models import (
    Wordpress,
    Soup
)
from .base_services import ResponseHandlerError
from .services import (
    WordpressResponseHandler,
    SoupResponseHandler
)


class IndexView(TemplateView):
    template_name = 'index.html'


# WORDPRESS #
class WordpressCreateView(FakeNewsCreateView):

    def __init__(self):
        super().__init__()
        self.template_name = 'wordpress/wordpress-create.html'
        self.form_class = WordpressCreateForm
        self.model = Wordpress

    def _run_handler(self, form):
        handler = WordpressResponseHandler(
            form.cleaned_data['url'],
            form.cleaned_data['f_source_type'],   # first
            form.cleaned_data['f_source_pattern'],
            form.cleaned_data['f_source_entire_link'],

            form.cleaned_data['s_source_type'],  # second
            form.cleaned_data['s_source_pattern'],
            form.cleaned_data['s_source_entire_link'],
        )
        try:
            result = handler.handle_response()
            self.context['task_ids'] = [result, result.parent]

        except ResponseHandlerError as err:
            form.add_error('url', str(err))


class WordpressUpdateView(FakeNewsUpdateView):

    def __init__(self):
        super().__init__()
        self.form_class = WordpressUpdateForm
        self.model = Wordpress
        self.template_name = 'wordpress/wordpress-update.html'

    def _run_handler(self, form):
        handler = WordpressResponseHandler(
            form.cleaned_data['url'],
            form.cleaned_data['f_source_type'],  # first
            form.cleaned_data['f_source_pattern'],
            form.cleaned_data['f_source_entire_link'],

            form.cleaned_data['s_source_type'],  # second
            form.cleaned_data['s_source_pattern'],
            form.cleaned_data['s_source_entire_link'],
        )
        # handle the output
        try:
            result = handler.handle_update_response()
            self.context['task_ids'] = [result, result.parent]

        except ResponseHandlerError as err:
            form.add_error('url', str(err))


class WordpressDetailView(FakeNewsDetailView):
    template_name = 'wordpress/wordpress-detail.html'
    model = Wordpress


class WordpressDeleteView(FakeNewsDeleteView):
    template_name = 'wordpress/wordpress-delete.html'
    model = Wordpress
    path_create = 'fakenews:wordpress-create'


class WordpressListView(FakeNewsListView):
    template_name = 'wordpress/wordpress-list.html'
    model = Wordpress
    context_object_name = 'wordpress'
    queryset = Wordpress.objects.all()


# POST #
class WordpressPostDownloadView(PostCreateView):
    template_name = 'wordpress/post-list.html'
    error_template_name = 'wordpress/wordpress-error.html'
    response_handler = WordpressResponseHandler
    model = Wordpress


class WordpressPostListView(PostListView):
    template_name = 'wordpress/post-list.html'
    response_handler = WordpressResponseHandler
    parent_model = Wordpress


# SOUP #
class SoupCreateView(FakeNewsCreateView):

    def __init__(self):
        super().__init__()
        self.template_name = 'soups/soup-create.html'
        self.form_class = SoupCreateForm
        self.model = Soup

    def _run_handler(self, form):
        handler = SoupResponseHandler(
            form.cleaned_data['url'],
            form.cleaned_data['f_source_type'],  # first
            form.cleaned_data['f_source_pattern'],
            form.cleaned_data['f_source_entire_link'],

            form.cleaned_data['s_source_type'],  # second
            form.cleaned_data['s_source_pattern'],
            form.cleaned_data['s_source_entire_link'],

            form.cleaned_data['link_class'],
            form.cleaned_data['date_type'],
            form.cleaned_data['date_id'],
            form.cleaned_data['body_class']
        )
        # handle the output
        try:
            result = handler.handle_response()
            self.context['task_id'] = result.task_id
        except ResponseHandlerError as err:
            form.add_error('url', str(err))


class SoupUpdateView(FakeNewsUpdateView):

    def __init__(self):
        super().__init__()
        self.form_class = SoupCreateForm
        self.model = Soup
        self.template_name = 'soups/soup-update.html'

    def _run_handler(self, form):
        handler = SoupResponseHandler(
            form.cleaned_data['url'],
            form.cleaned_data['f_source_type'],  # first
            form.cleaned_data['f_source_pattern'],
            form.cleaned_data['f_source_entire_link'],

            form.cleaned_data['s_source_type'],  # second
            form.cleaned_data['s_source_pattern'],
            form.cleaned_data['s_source_entire_link'],

            form.cleaned_data['link_class'],
            form.cleaned_data['date_type'],
            form.cleaned_data['date_id'],
            form.cleaned_data['body_class']
        )
        # handle the output
        try:
            result = handler.handle_update_response()
            self.context['task_id'] = result.task_id
        except ResponseHandlerError as err:
            form.add_error('url', str(err))


class SoupDetailView(FakeNewsDetailView):
    template_name = 'soups/soup-detail.html'
    model = Soup


class SoupDeleteView(FakeNewsDeleteView):
    template_name = 'soups/soup-delete.html'
    model = Soup
    path_create = 'fakenews:soup-create'


class SoupListView(FakeNewsListView):
    template_name = 'soups/soup-list.html'
    model = Soup
    context_object_name = 'soups'
    queryset = Soup.objects.all()


# POST #
class SoupPostDownloadView(PostCreateView):
    template_name = 'soups/post-list.html'
    error_template_name = 'soups/soup-error.html'
    response_handler = SoupResponseHandler
    model = Soup


class SoupPostListView(PostListView):
    template_name = 'soups/post-list.html'
    response_handler = SoupResponseHandler
    parent_model = Soup
