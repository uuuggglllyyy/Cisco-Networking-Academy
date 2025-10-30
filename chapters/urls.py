# chapters/urls.py - ДОБАВЛЯЕМ API URLS

from django.urls import path
from . import views

urlpatterns = [
    # СУЩЕСТВУЮЩИЕ URLS
    path('', views.module_list, name='module_list'),
    path('module/<int:module_id>/', views.module_detail, name='module_detail'),
    path('module/<int:module_id>/chapter/<int:chapter_id>/', views.chapter_detail, name='chapter_detail'),
    path('module/<int:module_id>/chapter/<int:chapter_id>/section/<int:section_id>/', views.section_detail,
         name='section_detail'),
    path('api/section/<int:section_id>/complete/', views.mark_section_completed, name='mark_section_completed'),


    # Управление прогрессом
    path('progress/', views.progress_management, name='progress_management'),
    path('api/progress/reset/', views.reset_progress, name='reset_progress'),
    path('api/progress/export/', views.export_progress, name='export_progress'),

    # AI Assistant URLs
    path('ai-assistant/', views.ai_chat_page, name='ai_assistant'),
    path('ai-assistant/module/<int:module_id>/', views.ai_chat_page, name='ai_assistant_module'),
    path('ai-assistant/module/<int:module_id>/chapter/<int:chapter_id>/', views.ai_chat_page,
         name='ai_assistant_chapter'),
    path('ai-assistant/module/<int:module_id>/chapter/<int:chapter_id>/section/<int:section_id>/', views.ai_chat_page,
         name='ai_assistant_section'),
    path('api/ai-assistant/', views.ai_assistant, name='ai_assistant_api'),

    # НОВЫЕ URLS ДЛЯ АУТЕНТИФИКАЦИИ И ОБРАТНОЙ СВЯЗИ
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-email/<str:token>/', views.verify_email_view, name='verify_email'),

    # Обратная связь
    path('feedback/', views.feedback_view, name='feedback'),
    path('my-feedback/', views.my_feedback_view, name='my_feedback'),

    # API для AJAX
    path('api/chapters/', views.get_chapters_by_module, name='get_chapters'),
    path('api/sections/', views.get_sections_by_chapter, name='get_sections'),
    path('api/user-profile/', views.user_profile_api, name='user_profile_api'),
]