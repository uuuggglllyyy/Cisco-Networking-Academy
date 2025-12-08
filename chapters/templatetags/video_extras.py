# chapters/templatetags/video_extras.py
import os
from django import template

register = template.Library()

@register.filter
def youtube_id(url):
    """Извлекает ID видео из YouTube URL"""
    import re
    patterns = [
        r'(?:youtube\.com\/watch\?v=|\/v\/|youtu\.be\/)([^&\n?#]+)',
        r'youtube\.com\/embed\/([^&\n?#]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ''

@register.filter
def vimeo_id(url):
    """Извлекает ID видео из Vimeo URL"""
    import re
    patterns = [
        r'vimeo\.com\/(\d+)',
        r'vimeo\.com\/video\/(\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ''

@register.filter
def filename(value):
    """Возвращает только имя файла из полного пути"""
    return os.path.basename(value)