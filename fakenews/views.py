from django.shortcuts import (
    render
)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from django.http import HttpResponseRedirect
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
    PostsResponseHandler,
    SoupResponseHandler
)
from .tasks import create_task


@csrf_exempt
def run_task(request):
    if request.POST:
        task_type = request.POST.get("type")
        task = create_task.delay(int(task_type))
        return JsonResponse({"task_id": task.id}, status=202)


class IndexView(TemplateView):
    template_name = 'index.html'


# WORDPRESS #
class WordpressCreateView(FakeNewsCreateView):
    template_name = 'wordpress/wordpress-create.html'
    form_class = WordpressCreateForm

    def _run_handler(self, form):
        handler = WordpressResponseHandler(
            form.cleaned_data['url']
        )
        # handle the output
        try:
            handler.handle_response()
        except ResponseHandlerError as err:
            form.add_error('url', str(err))


class WordpressUpdateView(FakeNewsUpdateView):
    template_name = 'wordpress/wordpress-update.html'
    form_class = WordpressUpdateForm
    model = Wordpress

    def _run_handler(self, form):
        handler = WordpressResponseHandler(
            form.cleaned_data['url']
        )
        # handle the output
        try:
            handler.handle_update_response()
        except ResponseHandlerError as err:
            form.add_error('url', str(err))


class WordpressDetailView(FakeNewsDetailView):
    template_name = 'wordpress/wordpress-detail.html'


class WordpressDeleteView(FakeNewsDeleteView):
    template_name = 'wordpress/wordpress-delete.html'
    model = Wordpress

    def get_success_url(self):
        return reverse('fakenews:wordpress-create')


class WordpressListView(FakeNewsListView):
    template_name = 'wordpress/wordpress-list.html'
    model = Wordpress
    context_object_name = 'wordpress'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse('fakenews:wordpress-create')
        return context


# POST #
class WordpressPostCreateView(PostCreateView):
    template_name = 'wordpress/post-list.html'
    error_template_name = 'wordpress/wordpress-error.html'
    model = Wordpress

    def _run_handler(self, request, obj):
        try:
            # get the input and delegate to process
            handler = WordpressResponseHandler(
                obj.url
            )
            handler.handle_download_response()
            return HttpResponseRedirect(
                reverse('fakenews:wordpress-post-list', kwargs={'id': obj.id})
            )
        except ResponseHandlerError as err:
            context = {
                'message': str(err)
            }
            return render(request, self.error_template_name, context)


class WordpressPostDownloadView(PostCreateView):
    template_name = 'wordpress/post-list.html'
    error_template_name = 'wordpress/wordpress-error.html'
    model = Wordpress

    def _run_handler(self, request, obj):
        try:
            # get the input and delegate to process
            handler = PostsResponseHandler(
                obj.url,
                obj.id
            )
            return handler.handle_download_response()
        except ResponseHandlerError as err:
            context = {
                'message': str(err)
            }
            return render(request, self.error_template_name, context)


class WordpressPostListView(PostListView):
    template_name = 'wordpress/post-list.html'

    def get_queryset(self):
        handler = WordpressResponseHandler()
        queryset = handler.get_queryset(self.kwargs.get("id"))

        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wordpress'] = Wordpress.objects.find_by_id(self.kwargs.get("id")).get()
        return context


# SOUP #
class SoupCreateView(FakeNewsCreateView):
    template_name = 'soups/soup-create.html'
    form_class = SoupCreateForm

    def _run_handler(self, form):
        handler = SoupResponseHandler(
            form.cleaned_data['url'],
            form.cleaned_data['link_class'],
            form.cleaned_data['date_type'],
            form.cleaned_data['date_id']
        )
        # handle the output
        try:
            handler.handle_response()
        except ResponseHandlerError as err:
            form.add_error('url', str(err))


class SoupUpdateView(FakeNewsUpdateView):
    template_name = 'soups/soup-update.html'
    form_class = SoupCreateForm
    model = Soup

    def _run_handler(self, form):
        handler = SoupResponseHandler(
            form.cleaned_data['url']
        )
        # handle the output
        try:
            handler.handle_update_response()
        except ResponseHandlerError as err:
            form.add_error('url', str(err))


class SoupDetailView(FakeNewsDetailView):
    template_name = 'soups/soup-detail.html'


class SoupDeleteView(FakeNewsDeleteView):
    template_name = 'soups/soup-delete.html'
    model = Soup

    def get_success_url(self):
        return reverse('fakenews:soup-create')


class SoupListView(FakeNewsListView):
    template_name = 'soups/soup-list.html'
    model = Soup
    context_object_name = 'soups'


# POST #
class SoupPostCreateView(PostCreateView):
    template_name = 'soups/post-list.html'
    error_template_name = 'soups/soup-error.html'
    model = Soup

    def _run_handler(self, request, obj):
        try:
            # get the input and delegate to process
            handler = SoupResponseHandler(
                obj.url,
                obj.link_class,
                obj.date_type,
                obj.date_id
            )
            handler.handle_update_response()
            return HttpResponseRedirect(reverse('fakenews:post-list', kwargs={'id': obj.id}))
        except ResponseHandlerError as err:
            context = {
                'message': str(err)
            }
            return render(request, self.error_template_name, context)


class SoupPostDownloadView(PostCreateView):
    template_name = 'soups/post-list.html'
    error_template_name = 'soups/soup-error.html'
    model = Soup

    def _run_handler(self, request, obj):
        try:
            # get the input and delegate to process
            handler = SoupResponseHandler(
                obj.url
            )
            return handler.handle_download_response()
        except ResponseHandlerError as err:
            context = {
                'message': str(err)
            }
            return render(request, self.error_template_name, context)


class SoupPostListView(PostListView):
    template_name = 'soups/post-list.html'

    def get_queryset(self):
        handler = SoupResponseHandler()
        queryset = handler.get_queryset(self.kwargs.get("id"))

        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['soup'] = Soup.objects.find_by_id(self.kwargs.get("id")).get()
        return context
