# test_email.py
import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ciscocourse.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings


def test_email():
    try:
        print("=== ТЕСТИРОВАНИЕ НАСТРОЕК EMAIL ===")
        print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
        print(f"EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
        print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        print("=" * 50)

        # Отправка тестового письма
        subject = 'Тестовое письмо от Cisco Academy'
        message = 'Это тестовое письмо для проверки настроек SMTP.'
        recipient_list = [settings.EMAIL_HOST_USER]  # Отправляем себе

        print(f"Отправка письма на: {recipient_list}")

        result = send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )

        print(f"✅ Письмо успешно отправлено! Результат: {result}")

    except Exception as e:
        print(f"❌ Ошибка при отправке письма: {e}")
        print(f"Тип ошибки: {type(e).__name__}")


if __name__ == "__main__":
    test_email()