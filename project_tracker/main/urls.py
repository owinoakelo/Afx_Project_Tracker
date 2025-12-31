from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('project/<uuid:uid>/', views.project_detail, name='project_detail'),
    path('project/<uuid:uid>/update/', views.project_update, name='project_update'),
]
