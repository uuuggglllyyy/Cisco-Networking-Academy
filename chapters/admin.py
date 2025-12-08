# admin.py - УПРОЩЕННАЯ ВЕРСИЯ БЕЗ ПРЕВЬЮ ВИДЕО
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from .models import Module, Chapter, Section, UserProfile, Feedback, FeedbackConfig, UserProgress


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 1


class SectionInline(admin.TabularInline):
    model = Section
    extra = 1
    fields = ['code', 'title', 'image', 'order']


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['number', 'title', 'order']
    inlines = [ChapterInline]


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['number', 'title', 'module', 'order']
    list_filter = ['module']
    inlines = [SectionInline]


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'chapter', 'has_video', 'order']
    list_filter = ['chapter__module', 'chapter']
    list_editable = ['order']
    readonly_fields = ['image_preview']  # ТОЛЬКО ПРЕВЬЮ ИЗОБРАЖЕНИЯ

    # ОБНОВЛЕННЫЙ FIELDSETS С ВИДЕО
    fieldsets = (
        ('Основная информация', {
            'fields': ('chapter', 'code', 'title', 'content', 'order')
        }),
        ('Медиа файлы', {
            'fields': ('image', 'image_preview', 'attached_file'),
            'classes': ('collapse',)
        }),
        ('Видео контент', {
            'fields': ('video_file', 'video_url'),
            'classes': ('collapse',)
        }),
        ('Ссылки', {
            'fields': ('external_link',),
            'classes': ('collapse',)
        }),
    )

    # ТОЛЬКО ПРЕВЬЮ ДЛЯ ИЗОБРАЖЕНИЯ
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 100px; max-width: 100px;" />')
        return "Нет изображения"
    image_preview.short_description = 'Превью изображения'

    def has_video(self, obj):
        return "✅" if obj.has_video else "❌"
    has_video.short_description = 'Видео'


# ОСТАЛЬНЫЕ КЛАССЫ АДМИНКИ БЕЗ ИЗМЕНЕНИЙ
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'
    fields = ('role', 'email_verified', 'phone', 'created_at')
    readonly_fields = ('created_at',)

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff')
    list_filter = ('profile__role', 'is_staff', 'is_superuser', 'is_active')

    def get_role(self, obj):
        return obj.profile.role if hasattr(obj, 'profile') else 'Нет профиля'

    get_role.short_description = 'Роль'


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['subject', 'user', 'feedback_type', 'status', 'created_at']
    list_filter = ['status', 'feedback_type', 'created_at']
    list_editable = ['status']
    search_fields = ['subject', 'message', 'user__username']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'feedback_type', 'subject', 'message', 'status')
        }),
        ('Связь с курсом', {
            'fields': ('module', 'chapter', 'section'),
            'classes': ('collapse',)
        }),
        ('Обработка', {
            'fields': ('admin_notes', 'created_at', 'updated_at')
        }),
    )


@admin.register(FeedbackConfig)
class FeedbackConfigAdmin(admin.ModelAdmin):
    list_display = ['notify_admins', 'auto_response_enabled', 'feedback_email']

    def has_add_permission(self, request):
        return not FeedbackConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'section', 'completed', 'time_spent', 'last_accessed']
    list_filter = ['completed', 'section__chapter__module', 'section__chapter']
    search_fields = ['user__username', 'section__title']


# ПЕРЕРЕГИСТРИРУЕМ ПОЛЬЗОВАТЕЛЯ
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)