from django.shortcuts import render, get_object_or_404
from .models import Chapter, Section

def chapter_list(request):
    chapters = Chapter.objects.all()
    return render(request, 'chapters/chapter_list.html', {'chapters': chapters})

def chapter_detail(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)
    sections = chapter.sections.all()
    return render(request, 'chapters/chapter_detail.html', {
        'chapter': chapter,
        'sections': sections
    })

def section_detail(request, chapter_id, section_id):
    section = get_object_or_404(Section, id=section_id, chapter_id=chapter_id)
    return render(request, 'chapters/section_detail.html', {'section': section})