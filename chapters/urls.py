from django.urls import path
from . import views

urlpatterns = [
    path('', views.module_list, name='module_list'),
    path('module/<int:module_id>/', views.module_detail, name='module_detail'),
    path('module/<int:module_id>/chapter/<int:chapter_id>/', views.chapter_detail, name='chapter_detail'),
    path('module/<int:module_id>/chapter/<int:chapter_id>/section/<int:section_id>/', views.section_detail, name='section_detail'),
]