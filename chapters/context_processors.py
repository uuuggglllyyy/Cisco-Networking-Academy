# chapters/context_processors.py

from .models import Module
from .views import get_user_progress


def global_context(request):
    modules = Module.objects.all()
    total_progress = get_user_progress(request.user)

    return {
        'modules': modules,
        'total_progress': total_progress
    }