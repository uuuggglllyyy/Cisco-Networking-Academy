# chapters/test_utils.py
from django.contrib.auth.models import User
from .models import UserProfile


def get_or_create_test_user():
    """Создает или получает тестового пользователя"""
    user, created = User.objects.get_or_create(
        username='demo_user',
        defaults={
            'email': 'demo@example.com',
            'first_name': 'Демо',
            'last_name': 'Пользователь',
            'is_active': True,
            'is_staff': False,
            'is_superuser': False
        }
    )

    if created:
        user.set_password('demo123')  # Простой пароль для тестирования
        user.save()
        print(f"Создан тестовый пользователь: {user.username}")

    # Создаем профиль если его нет
    profile, profile_created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'email_verified': True,
            'role': 'student'
        }
    )

    return user


def get_test_user(request):
    """Возвращает тестового пользователя или None"""
    from django.conf import settings
    if getattr(settings, 'TEST_MODE', False) and not request.user.is_authenticated:
        return get_or_create_test_user()
    return request.user