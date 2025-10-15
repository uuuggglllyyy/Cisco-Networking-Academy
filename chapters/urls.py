from django.urls import path
from . import views

urlpatterns = [
    path('', views.chapter_list, name='chapter_list'),
    path('chapter/<int:chapter_id>/', views.chapter_detail, name='chapter_detail'),
    path('chapter/<int:chapter_id>/section/<int:section_id>/', views.section_detail, name='section_detail'),
]