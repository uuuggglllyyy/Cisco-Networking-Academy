from django.shortcuts import render, get_object_or_404
from .models import Module, Chapter, Section

def module_list(request):
    modules = Module.objects.all()
    return render(request, 'chapters/module_list.html', {'modules': modules})

def module_detail(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    chapters = module.chapters.all()
    return render(request, 'chapters/module_detail.html', {
        'module': module,
        'chapters': chapters
    })

def chapter_detail(request, module_id, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id, module_id=module_id)
    sections = chapter.sections.all()
    return render(request, 'chapters/chapter_detail.html', {
        'chapter': chapter,
        'sections': sections
    })

def section_detail(request, module_id, chapter_id, section_id):
    section = get_object_or_404(Section, id=section_id, chapter_id=chapter_id, chapter__module_id=module_id)
    return render(request, 'chapters/section_detail.html', {'section': section})