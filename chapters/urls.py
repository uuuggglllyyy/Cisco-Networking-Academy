from django.urls import path
from . import views

urlpatterns = [
    path('', views.module_list, name='module_list'),
    path('module/<int:module_id>/', views.module_detail, name='module_detail'),
    path('module/<int:module_id>/chapter/<int:chapter_id>/', views.chapter_detail, name='chapter_detail'),
    path('module/<int:module_id>/chapter/<int:chapter_id>/section/<int:section_id>/', views.section_detail,
         name='section_detail'),

    # AI Assistant URLs - ИСПРАВЛЕННЫЕ ИМЕНА ФУНКЦИЙ
    path('ai-assistant/', views.ai_chat_page, name='ai_assistant'),
    path('ai-assistant/module/<int:module_id>/', views.ai_chat_page, name='ai_assistant_module'),
    path('ai-assistant/module/<int:module_id>/chapter/<int:chapter_id>/', views.ai_chat_page,
         name='ai_assistant_chapter'),
    path('ai-assistant/module/<int:module_id>/chapter/<int:chapter_id>/section/<int:section_id>/', views.ai_chat_page,
         name='ai_assistant_section'),
    path('api/ai-assistant/', views.ai_assistant, name='ai_assistant_api'),
]