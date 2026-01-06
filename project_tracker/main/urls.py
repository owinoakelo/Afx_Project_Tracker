from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('project/<uuid:uid>/', views.project_detail, name='project_detail'),
    path('project/<uuid:uid>/update/', views.project_update, name='project_update'),
    path('category/<uuid:uid>/', views.category_detail, name='category_detail'),
    path('category/<uuid:uid>/update/', views.category_update, name='category_update'),
    path('category/create/', views.category_create, name='category_create'),
    path('project/create/<uuid:cat_uid>', views.project_create, name='project_create'),
]
