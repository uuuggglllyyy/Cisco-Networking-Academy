# chapters/feedback_utils.py
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from .models import FeedbackConfig


def get_feedback_config():
    """Получает или создает настройки обратной связи"""
    config, created = FeedbackConfig.objects.get_or_create(
        defaults={
            'notify_admins': True,
            'auto_response_enabled': True,
            'feedback_email': 'great.egor7288@yandex.ru',
        }
    )
    return config


def send_feedback_notifications(feedback):
    """Отправляет уведомления о новой обратной связи"""
    config = get_feedback_config()
    recipients = []

    # Администраторы системы
    if config.notify_admins:
        admin_users = User.objects.filter(is_staff=True, is_active=True)
        admin_emails = [user.email for user in admin_users if user.email]
        recipients.extend(admin_emails)

    # Дополнительные email из настроек
    additional_emails = config.get_notify_emails_list()
    recipients.extend(additional_emails)

    # Убираем дубликаты
    recipients = list(set(recipients))

    if not recipients:
        print("⚠️ Нет получателей для уведомлений")
        return

    try:
        subject = f'📝 Новая обратная связь: {feedback.subject}'

        html_message = render_to_string('chapters/emails/feedback_notification.html', {
            'feedback': feedback,
            'recipient_count': len(recipients),
            'config': config,
        })
        plain_message = strip_tags(html_message)

        send_mail(
            subject,
            plain_message,
            config.feedback_email,  # Используем email из настроек
            recipients,
            html_message=html_message,
            fail_silently=False,
        )

        print(f"✅ Уведомления отправлены {len(recipients)} получателям")

    except Exception as e:
        print(f"❌ Ошибка отправки уведомлений: {e}")


def send_feedback_auto_response(feedback):
    """Отправляет авто-ответ пользователю"""
    config = get_feedback_config()

    if not config.auto_response_enabled:
        return

    try:
        subject = config.auto_response_subject
        message = config.auto_response_message

        # Добавляем информацию об обращении
        full_message = f"""{message}

Детали вашего обращения:
- Номер: #{feedback.id}
- Тема: {feedback.subject}
- Тип: {feedback.get_feedback_type_display()}
- Дата: {feedback.created_at.strftime('%d.%m.%Y %H:%M')}

Мы свяжемся с вами в ближайшее время.

С уважением,
Команда Cisco Networking Academy"""

        send_mail(
            subject,
            full_message,
            config.feedback_email,
            [feedback.user.email],
            fail_silently=False,
        )

        print(f"✅ Авто-ответ отправлен пользователю {feedback.user.email}")

    except Exception as e:
        print(f"❌ Ошибка отправки авто-ответа: {e}")