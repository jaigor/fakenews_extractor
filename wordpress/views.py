from django.shortcuts import (
    render, 
    get_object_or_404
)
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView
)
from django.urls import reverse
from django.http import HttpResponseRedirect

from .forms import (
    WordpressCreateForm, 
    WordpressUpdateForm
)
from .models import (
    Wordpress, 
    Post
)
from .services import (
    TypesResponseHandler, 
    PostsResponseHandler,
    ResponseHandlerError
)
############## WORDPRESS ##############
class WordpressCreateView(CreateView):
    template_name = 'wordpress/wordpress-create.html'
    form_class = WordpressCreateForm

    def get_success_url(self):
        return '/'
    
    def form_valid(self, form):
        return super().form_valid(form)

    # GET Method
    def get(self, request, *args, **kwargs):
        form = WordpressCreateForm()
        context = {
            'form': form
            }
        return render(request, self.template_name, context)
        
    # POST Method
    def post(self, request, *args, **kwargs):
        form = WordpressCreateForm(request.POST or None)

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
        handler = TypesResponseHandler(
            form.cleaned_data['url']
        )
        # handle the output
        try:
            handler.handle_types_response()
        except ResponseHandlerError as err:
            form.add_error('url', str(err))

class WordpressUpdateView(UpdateView):
    template_name = 'wordpress/wordpress-update.html'
    form_class = WordpressUpdateForm
    model = Wordpress

    def get_success_url(self):
        return '/'
    
    def form_valid(self, form):
        return super().form_valid(form)

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Wordpress, id=id_)

    # GET Method
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        form = WordpressUpdateForm(instance=obj)
        context = {
            'object': obj,
            'form': form
        }
        return render(request, self.template_name, context)

    # POST Method
    def post(self, request, *args, **kwargs):
        obj = self.get_object()

        form = WordpressUpdateForm(request.POST or None, instance=obj)
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
        handler = TypesResponseHandler(
            form.cleaned_data['url']
        )
        # handle the output
        try:
            handler.handle_types_response()
        except ResponseHandlerError as err:
            form.add_error('url', str(err))

class WordpressDetailView(DetailView):
    template_name = 'wordpress/wordpress-detail.html'

    def get_success_url(self):
        return '/'

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Wordpress, id=id_)

    # GET Method
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        context = {
            'object': obj
        }
        return render(request, self.template_name, context)
            
class WordpressDeleteView(DeleteView):
    template_name = 'wordpress/wordpress-delete.html'
    model = Wordpress

    def get_success_url(self):
        return reverse('wordpress:wordpress-create')
    
    def form_valid(self, form):
        return super().form_valid(form)

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Wordpress, id=id_)

class WordpressListView(ListView):
    template_name = 'wordpress/wordpress-list.html'
    paginate_by = 10  # if pagination is desired
    model = Wordpress
    context_object_name = 'wordpress'
    queryset = Wordpress.objects.all()
    ordering = ['-id']

############## POST ##############

class PostCreateView(DetailView):
    template_name = 'wordpress/post-list.html'
    error_template_name = 'wordpress/wordpress-error.html'

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Wordpress, id=id_)

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
            return HttpResponseRedirect(reverse('wordpress:post-list', kwargs={'id': obj.id}))
        except ResponseHandlerError as err:
            context = {
                'message': str(err)
            }
            return render(request, self.error_template_name, context)

    def _run_handler(self, obj):        
        handler = PostsResponseHandler(
            obj.url,
            obj.id
        )
        handler.handle_post_response()

class PostDownloadView(DetailView):
    template_name = 'wordpress/post-list.html'
    error_template_name = 'wordpress/wordpress-error.html'

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Wordpress, id=id_)

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
        handler = PostsResponseHandler(
            obj.url,
            obj.id
        )
        return handler.handle_download_response()

class PostListView(ListView):
    template_name = 'wordpress/post-list.html'
    paginate_by = 10  # if pagination is desired
    model = Post
    context_object_name = 'posts'
    ordering = ['-id']    

    def get_queryset(self):
        handler = PostsResponseHandler(
            wordpress_id=self.kwargs.get("id")
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
        context['wordpress'] = Wordpress.objects.find_by_id(self.kwargs.get("id")).get()
        return context