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

from .forms import (
    FakeNewsForm
)
from .models import (
    FakeNews,
    Post
)
### Interfaces ####
class FakeNewsCreateView(CreateView):

    def get_success_url(self):
        return '/'
    
    def form_valid(self, form):
        return super().form_valid(form)

    # GET Method
    def get(self, request, *args, **kwargs):
        form = FakeNewsForm()
        context = {
            'form': form
            }
        return render(request, self.template_name, context)
        
    # POST Method
    def post(self, request, *args, **kwargs):
        form = FakeNewsForm(request.POST or None)

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

class FakeNewsUpdateView(UpdateView):

    def get_success_url(self):
        return '/'
    
    def form_valid(self, form):
        return super().form_valid(form)

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(FakeNews, id=id_)

    # GET Method
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        form = FakeNewsForm(instance=obj)
        context = {
            'object': obj,
            'form': form
        }
        return render(request, self.template_name, context)

    # POST Method
    def post(self, request, *args, **kwargs):
        obj = self.get_object()

        form = FakeNewsForm(request.POST or None, instance=obj)
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

class FakeNewsDetailView(DetailView):

    def get_success_url(self):
        return '/'

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(FakeNews, id=id_)

    # GET Method
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        context = {
            'object': obj
        }
        return render(request, self.template_name, context)

class FakeNewsDeleteView(DeleteView):
    
    def form_valid(self, form):
        return super().form_valid(form)

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(FakeNews, id=id_)

class FakeNewsListView(ListView):
    paginate_by = 10  # if pagination is desired
    queryset = FakeNews.objects.all()
    ordering = ['-id']

############## POST ##############

class PostCreateView(DetailView):

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(FakeNews, id=id_)

    # GET Method
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        # handle the output
        return self._run_handler(request, obj)

class PostListView(ListView):
    paginate_by = 10  # if pagination is desired
    model = Post
    context_object_name = 'posts'
    ordering = ['-id']