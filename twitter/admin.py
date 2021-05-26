from django.contrib import admin
from .models import Tweet, User, Query

# Register your models here.
admin.site.register(Query)
admin.site.register(Tweet)
admin.site.register(User)