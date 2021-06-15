from django.shortcuts import render
from django.views.generic import (
    DetailView,
    ListView
)


# Social Element #
class SocialCreateView(DetailView):
    response_handler = None
    error_template_name = None
    exception = None

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        # handle the output
        return self._run_handler(request, obj)

    def _run_handler(self, request, obj):
        try:
            # get the input and delegate to process
            handler = self.response_handler(
                obj.text
            )
            return handler.handle_download_response()
        except self.exception as err:
            context = {
                'message': str(err)
            }
            return render(request, self.error_template_name, context)


class SocialListView(ListView):
    paginate_by = 10  # if pagination is desired
    ordering = ['-id']
    response_handler = None
    parent_model = None
    object_name = ''

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
        context[self.object_name] = self.parent_model.objects.find_by_id(self.kwargs.get("pk")).get()
        return context
