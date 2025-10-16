from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import requests
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.utils.html import escape
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


# УБЕДИТЕСЬ ЧТО ЭТА ФУНКЦИЯ ЕСТЬ В ФАЙЛЕ!
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