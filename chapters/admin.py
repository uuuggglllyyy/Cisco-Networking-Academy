# chapters/admin.py - ДОБАВЛЯЕМ В СУЩЕСТВУЮЩИЙ ФАЙЛ

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Module, Chapter, Section, UserProfile, Feedback, FeedbackConfig


# СУЩЕСТВУЮЩИЕ КЛАССЫ ОСТАЮТСЯ
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
    list_display = ['code', 'title', 'chapter', 'external_link', 'attached_file', 'order']
    list_filter = ['chapter__module', 'chapter']
    list_editable = ['order']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 50px; max-width: 50px;" />'
        return "Нет изображения"

    image_preview.short_description = 'Превью'
    image_preview.allow_tags = True


# НОВЫЕ КЛАССЫ АДМИНКИ
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'


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


# ПЕРЕРЕГИСТРИРУЕМ ПОЛЬЗОВАТЕЛЯ
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(FeedbackConfig)
class FeedbackConfigAdmin(admin.ModelAdmin):
    list_display = ['notify_admins', 'auto_response_enabled', 'feedback_email']

    def has_add_permission(self, request):
        # Разрешаем создавать только одну запись
        return not FeedbackConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False