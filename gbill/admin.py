from django.contrib import admin

from .models import Person, Item, Bill

# Register your models here.
admin.site.register([Person, Item, Bill])