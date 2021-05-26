from django.contrib import admin
from .models import Wordpress, Soup, Post

# Register your models here.
admin.site.register(Wordpress)
admin.site.register(Soup)
admin.site.register(Post)