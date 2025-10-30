from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import requests
import secrets
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Module, Chapter, Section, UserProfile, Feedback, UserProgress
from .forms import RegistrationForm, FeedbackForm
from django.http import JsonResponse
from .feedback_utils import send_feedback_notifications, send_feedback_auto_response


def module_list(request):
    modules = Module.objects.all()

    # Получаем общий прогресс
    total_progress = get_user_progress(request.user)

    # Получаем прогресс по каждому модулю
    modules_with_progress = []
    for module in modules:
        module_progress = get_user_progress(request.user, module=module)
        modules_with_progress.append({
            'module': module,
            'progress': module_progress
        })

    return render(request, 'chapters/module_list.html', {
        'modules_with_progress': modules_with_progress,
        'total_progress': total_progress
    })


def module_detail(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    chapters = module.chapters.all()

    # Получаем прогресс для каждой главы
    chapters_with_progress = []
    for chapter in chapters:
        chapter_progress = get_user_progress(request.user, chapter=chapter)
        # Добавляем прогресс к объекту главы
        chapter.progress = chapter_progress
        chapters_with_progress.append(chapter)

    module_progress = get_user_progress(request.user, module=module)

    return render(request, 'chapters/module_detail.html', {
        'module': module,
        'chapters': chapters_with_progress,  # Используем обновленный список
        'module_progress': module_progress
    })


def chapter_detail(request, module_id, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id, module_id=module_id)
    sections = chapter.sections.all()

    chapter_progress = get_user_progress(request.user, chapter=chapter)

    # Получаем статус для каждого раздела с информацией о прогрессе
    sections_with_progress = []
    for section in sections:
        if request.user.is_authenticated:
            progress = UserProgress.objects.filter(user=request.user, section=section).first()
            if progress and progress.completed:
                status = 'completed'
                status_text = '✓ Пройден'
            else:
                status = 'not-started'
                status_text = '● Не пройден'
        else:
            status = 'not-started'
            status_text = '● Не пройден'

        sections_with_progress.append({
            'section': section,
            'status': status,
            'status_text': status_text,
            'progress': progress
        })

    return render(request, 'chapters/chapter_detail.html', {
        'chapter': chapter,
        'sections_with_progress': sections_with_progress,
        'chapter_progress': chapter_progress
    })


def section_detail(request, module_id, chapter_id, section_id):
    section = get_object_or_404(Section, id=section_id, chapter_id=chapter_id, chapter__module_id=module_id)

    # Расчет времени чтения
    reading_time = calculate_reading_time(section.content)

    # Автоматически отмечаем раздел как прочитанный при открытии (но не сразу)
    user_progress = None
    was_newly_marked = False

    if request.user.is_authenticated:
        user_progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            section=section
        )

        # Если прогресс еще не отмечен, мы его отметим через JavaScript с задержкой
        # или при закрытии страницы
        if not user_progress.completed:
            # Здесь мы НЕ сохраняем сразу, а оставляем для JavaScript
            pass

    # Получаем прогресс по главе
    chapter_progress = get_user_progress(request.user, chapter=section.chapter)

    return render(request, 'chapters/section_detail.html', {
        'section': section,
        'reading_time': reading_time,
        'user_progress': user_progress,
        'chapter_progress': chapter_progress
    })

@csrf_exempt
@require_http_methods(["POST"])
def ai_assistant(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        user_message = data.get('message', '').strip().lower()

        # Быстрые предопределенные ответы для частых вопросов
        quick_responses = {
            "как настроить айпи у маршрутизатора": "Для настройки IP на маршрутизаторе Cisco:\n1. Зайдите в режим конфигурации: enable → configure terminal\n2. Выберите интерфейс: interface gigabitethernet0/0\n3. Назначьте IP: ip address 192.168.1.1 255.255.255.0\n4. Включите интерфейс: no shutdown",

            "как настроить ip на маршрутизаторе": "Настройка IP адреса на маршрутизаторе Cisco:\n- interface <interface_name>\n- ip address <ip> <mask>\n- no shutdown",

            "что такое tcp/ip": "TCP/IP - это набор сетевых протоколов для передачи данных в интернете. Состоит из:\n- TCP (Transmission Control Protocol) - надежная передача\n- IP (Internet Protocol) - маршрутизация пакетов",

            "модель osi": "Модель OSI имеет 7 уровней:\n7. Прикладной (Application)\n6. Представления (Presentation)\n5. Сеансовый (Session)\n4. Транспортный (Transport)\n3. Сетевой (Network)\n2. Канальный (Data Link)\n1. Физический (Physical)",

            "разница между коммутатором и маршрутизатором": "Коммутатор работает на 2 уровне (Data Link), маршрутизатор на 3 уровне (Network). Коммутатор соединяет устройства в LAN, маршрутизатор соединяет разные сети.",
        }

        # Проверяем есть ли быстрый ответ
        for question, answer in quick_responses.items():
            if question in user_message:
                return JsonResponse({'response': answer})

        # Если нет быстрого ответа, пробуем Ollama
        prompt = f"Кратко ответь на вопрос по сетевым технологиям: {user_message}"

        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama2:7b',
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.3,
                    'max_tokens': 300
                }
            },
            timeout=90
        )

        if response.status_code == 200:
            result = response.json()
            return JsonResponse({'response': result.get('response', 'Ответ получен')})
        else:
            return JsonResponse({
                'response': "Попробуйте переформулировать вопрос или обратиться к материалам курса."
            })

    except requests.exceptions.Timeout:
        return JsonResponse({
            'response': "Для настройки IP на маршрутизаторе Cisco используйте команды:\n- interface <interface>\n- ip address <ip> <mask>\n- no shutdown\n\nПодробнее в модуле 2 курса Cisco."
        })
    except Exception as e:
        return JsonResponse({
            'response': f"Вопрос получен: {user_message}. Для деталей обратитесь к материалам курса Cisco."
        })


def ai_chat_page(request, module_id=None, chapter_id=None, section_id=None):
    """
    Страница чата с AI ассистентом
    """
    context = {}

    # Добавляем контекст в зависимости от текущей позиции в курсе
    if module_id:
        module = get_object_or_404(Module, id=module_id)
        context['current_module'] = module.title
        context['module_id'] = module_id

    if chapter_id:
        chapter = get_object_or_404(Chapter, id=chapter_id, module_id=module_id)
        context['current_chapter'] = chapter.title
        context['chapter_id'] = chapter_id

    if section_id:
        section = get_object_or_404(
            Section,
            id=section_id,
            chapter_id=chapter_id,
            chapter__module_id=module_id
        )
        context['current_section'] = section.title
        context['section_id'] = section_id

    return render(request, 'chapters/ai_assistant.html', context)


# НОВЫЕ ФУНКЦИИ ДЛЯ АУТЕНТИФИКАЦИИ
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = False  # Пользователь не активен до подтверждения email
                user.save()

                # Создаем профиль
                profile = user.profile
                profile.verification_token = secrets.token_urlsafe(32)
                profile.save()

                # Отправляем email подтверждения
                send_verification_email(user, profile.verification_token)

                return render(request, 'chapters/registration/registration_success.html')

            except Exception as e:
                # Логируем ошибку
                print(f"Ошибка при регистрации: {e}")
                return render(request, 'chapters/registration/register.html', {
                    'form': form,
                    'error': 'Произошла ошибка при регистрации. Попробуйте еще раз.'
                })
    else:
        form = RegistrationForm()

    return render(request, 'chapters/registration/register.html', {'form': form})


def send_verification_email(user, token):
    try:
        verification_url = f"http://ktpt.fun:50005/verify-email/{token}/"

        subject = 'Подтверждение email - Cisco Networking Academy'
        html_message = render_to_string('chapters/emails/verification_email.html', {
            'user': user,
            'verification_url': verification_url,
        })
        plain_message = strip_tags(html_message)

        # В режиме разработки просто выводим ссылку в консоль
        if settings.DEBUG:
            print(f"Ссылка для подтверждения: {verification_url}")
        else:
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
            )

    except Exception as e:
        print(f"Ошибка отправки email: {e}")


def verify_email_view(request, token):
    try:
        profile = UserProfile.objects.get(verification_token=token)
        user = profile.user
        user.is_active = True
        user.save()

        profile.email_verified = True
        profile.verification_token = None
        profile.save()

        return render(request, 'chapters/registration/verification_success.html')
    except UserProfile.DoesNotExist:
        return render(request, 'chapters/registration/verification_error.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                next_url = request.GET.get('next', '/')
                return redirect(next_url)
            else:
                return render(request, 'chapters/auth/login.html', {
                    'error': 'Аккаунт не активирован. Проверьте вашу почту для подтверждения.'
                })
        else:
            return render(request, 'chapters/auth/login.html', {
                'error': 'Неверное имя пользователя или пароль.'
            })

    return render(request, 'chapters/auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('/')


# API для получения глав по модулю
def get_chapters_by_module(request):
    module_id = request.GET.get('module')
    if module_id:
        chapters = Chapter.objects.filter(module_id=module_id).values('id', 'number', 'title')
        return JsonResponse({'chapters': list(chapters)})
    return JsonResponse({'chapters': []})


# API для получения разделов по главе
def get_sections_by_chapter(request):
    chapter_id = request.GET.get('chapter')
    if chapter_id:
        sections = Section.objects.filter(chapter_id=chapter_id).values('id', 'code', 'title')
        return JsonResponse({'sections': list(sections)})
    return JsonResponse({'sections': []})


def calculate_reading_time(text):
    """Рассчитывает время чтения в минутах"""
    # Средняя скорость чтения: 200-250 слов в минуту
    words = len(text.split())
    reading_time = max(1, round(words / 200))  # минимум 1 минута
    return reading_time


def get_user_progress(user, chapter=None, module=None):
    """Получает прогресс пользователя"""
    if not user.is_authenticated:
        return {
            'completed_sections': 0,
            'total_sections': 0,
            'progress_percentage': 0
        }

    if chapter:
        sections = Section.objects.filter(chapter=chapter)
    elif module:
        sections = Section.objects.filter(chapter__module=module)
    else:
        sections = Section.objects.all()

    total_sections = sections.count()
    completed_sections = UserProgress.objects.filter(
        user=user,
        section__in=sections,
        completed=True
    ).count()

    progress_percentage = round((completed_sections / total_sections) * 100) if total_sections > 0 else 0

    return {
        'completed_sections': completed_sections,
        'total_sections': total_sections,
        'progress_percentage': progress_percentage
    }


# ФУНКЦИИ ДЛЯ ОБРАТНОЙ СВЯЗИ
@login_required
def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            try:
                feedback = form.save(commit=False)
                feedback.user = request.user
                feedback.save()

                # ВСЕГДА отправляем уведомления
                send_feedback_notifications(feedback)

                # Отправляем авто-ответ пользователю
                send_feedback_auto_response(feedback)

                return render(request, 'chapters/feedback/feedback_success.html')

            except Exception as e:
                print(f"Ошибка при сохранении обратной связи: {e}")
                return render(request, 'chapters/feedback/feedback_form.html', {
                    'form': form,
                    'error': 'Произошла ошибка при отправке обращения.'
                })
    else:
        form = FeedbackForm()

    return render(request, 'chapters/feedback/feedback_form.html', {'form': form})


@login_required
def my_feedback_view(request):
    feedbacks = Feedback.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'chapters/feedback/my_feedback.html', {'feedbacks': feedbacks})


# API ДЛЯ ПРОВЕРКИ СТАТУСА ПОЛЬЗОВАТЕЛЯ
@login_required
def user_profile_api(request):
    profile = request.user.profile
    return JsonResponse({
        'username': request.user.username,
        'email': request.user.email,
        'role': profile.role,
        'email_verified': profile.email_verified,
    })


@login_required
@require_http_methods(["POST"])
def mark_section_completed(request, section_id):
    """Отмечает раздел как пройденный"""
    section = get_object_or_404(Section, id=section_id)

    progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        section=section
    )
    progress.completed = True
    progress.save()

    return JsonResponse({'status': 'success'})


@login_required
def progress_management(request):
    """Страница управления прогрессом"""
    total_progress = get_user_progress(request.user)
    return render(request, 'chapters/progress_management.html', {
        'total_progress': total_progress
    })


@login_required
@require_http_methods(["POST"])
def reset_progress(request):
    """Сброс всего прогресса пользователя"""
    try:
        # Удаляем все записи прогресса пользователя
        deleted_count, _ = UserProgress.objects.filter(user=request.user).delete()

        return JsonResponse({
            'status': 'success',
            'message': f'Удалено {deleted_count} записей прогресса',
            'deleted_count': deleted_count
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
def export_progress(request):
    """Экспорт прогресса пользователя"""
    progress_data = UserProgress.objects.filter(user=request.user).select_related('section', 'section__chapter',
                                                                                  'section__chapter__module')

    export_data = {
        'user': request.user.username,
        'export_date': timezone.now().isoformat(),
        'progress': []
    }

    for progress in progress_data:
        export_data['progress'].append({
            'module': progress.section.chapter.module.title,
            'module_number': progress.section.chapter.module.number,
            'chapter': progress.section.chapter.title,
            'chapter_number': progress.section.chapter.number,
            'section': progress.section.title,
            'section_code': progress.section.code,
            'completed': progress.completed,
            'time_spent': progress.time_spent,
            'last_accessed': progress.last_accessed.isoformat(),
            'created_at': progress.created_at.isoformat()
        })

    return JsonResponse(export_data)