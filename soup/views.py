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

from .forms import SoupCreateForm
from .models import (
    Soup, 
    Post
)
from .services import (
    SoupResponseHandler,
    PostsResponseHandler, 
    ResponseHandlerError
)

class SoupCreateView(CreateView):
    template_name = 'soups/soup-create.html'
    form_class = SoupCreateForm

    def get_success_url(self):
        return '/'
    
    def form_valid(self, form):
        return super().form_valid(form) 

    # GET Method
    def get(self, request, *args, **kwargs):
        form = SoupCreateForm()
        context = {
            'form': form
            }
        return render(request, self.template_name, context)
        
    # POST Method
    def post(self, request, *args, **kwargs):
        form = SoupCreateForm(request.POST or None)

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

class SoupUpdateView(UpdateView):
    template_name = 'soups/soup-update.html'
    form_class = SoupCreateForm

    def get_success_url(self):
        return '/'
    
    def form_valid(self, form):
        return super().form_valid(form)

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Soup, id=id_)

    # GET Method
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        form = SoupCreateForm(instance=obj)
        context = {
            'object': obj,
            'form': form
            }
        return render(request, self.template_name, context)

    # POST Method
    def post(self, request, *args, **kwargs):
        obj = self.get_object()

        form = SoupCreateForm(request.POST or None, instance=obj)
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
        handler = SoupResponseHandler(
            form.cleaned_data['url']
        )
        # handle the output
        try:
            handler.handle_update_response()
        except ResponseHandlerError as err:
            form.add_error('url', str(err))

class SoupDetailView(DetailView):
    template_name = 'soups/soup-detail.html'

    def get_success_url(self):
        return '/'

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Soup, id=id_)

    # GET Method
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        context = {
            'object': obj
        }
        return render(request, self.template_name, context)

class SoupDeleteView(DeleteView):
    template_name = 'soups/soup-delete.html'    
    model = Soup

    def get_success_url(self):
        return reverse('soup:soup-create')
    
    def form_valid(self, form):
        return super().form_valid(form)

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Soup, id=id_)

class SoupListView(ListView):
    template_name = 'soups/soup-list.html'
    paginate_by = 10  # if pagination is desired
    model = Soup
    context_object_name = 'soups'
    queryset = Soup.objects.all()
    ordering = ['-id']

############## POST ##############

class PostCreateView(DetailView):
    template_name = 'soups/post-list.html'
    error_template_name = 'soups/soup-error.html'

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Soup, id=id_)

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
            return HttpResponseRedirect(reverse('soup:post-list', kwargs={'id': obj.id}))
        except ResponseHandlerError as err:
            context = {
                'message': str(err)
            }
            return render(request, self.error_template_name, context)

    def _run_handler(self, obj):        
        handler = SoupResponseHandler(
            obj.url,
            obj.link_class,
            obj.date_type,
            obj.date_id
        )
        handler.handle_update_response()

class PostDownloadView(DetailView):
    template_name = 'soups/post-list.html'
    error_template_name = 'soups/soup-error.html'

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Soup, id=id_)

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
        handler = SoupResponseHandler(
            obj.url
        )
        return handler.handle_download_response()

class PostListView(ListView):
    template_name = 'soups/post-list.html'
    paginate_by = 10  # if pagination is desired
    model = Post
    context_object_name = 'posts'
    ordering = ['-id']    

    def get_queryset(self):
        handler = PostsResponseHandler(
            soup_id=self.kwargs.get("id")
        )
        queryset = handler.get_queryset()

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