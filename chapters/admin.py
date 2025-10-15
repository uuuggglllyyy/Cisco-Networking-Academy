from django.contrib import admin
from .models import Chapter, Section

class SectionInline(admin.TabularInline):
    model = Section
    extra = 1

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['number', 'title', 'order']
    inlines = [SectionInline]

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'chapter', 'order']
    list_filter = ['chapter']