from django.contrib import admin
from .models import Module, Chapter, Section

class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 1

class SectionInline(admin.TabularInline):
    model = Section
    extra = 1
    fields = ['code', 'title', 'image', 'order']  # Добавляем изображение в список полей


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