from django.contrib import admin
from .models import Category, Status, Project

# Register your models here.
admin.site.register(Category)
admin.site.register(Status)
admin.site.register(Project)