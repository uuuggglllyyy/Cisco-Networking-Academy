from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Module(models.Model):
    number = models.IntegerField(verbose_name="Номер модуля")
    title = models.CharField(max_length=200, verbose_name="Название модуля")
    description = models.TextField(blank=True, verbose_name="Описание")
    order = models.IntegerField(default=0, verbose_name="Порядок")

    class Meta:
        ordering = ['order']
        verbose_name = 'Модуль'
        verbose_name_plural = 'Модули'

    def __str__(self):
        return f"Модуль {self.number}. {self.title}"


class Chapter(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='chapters')
    number = models.IntegerField(verbose_name="Номер главы")
    title = models.CharField(max_length=200, verbose_name="Название главы")
    description = models.TextField(blank=True, verbose_name="Описание")
    order = models.IntegerField(default=0, verbose_name="Порядок")

    class Meta:
        ordering = ['order']
        verbose_name = 'Глава'
        verbose_name_plural = 'Главы'

    def __str__(self):
        return f"Глава {self.number}. {self.title}"


class Section(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='sections')
    code = models.CharField(max_length=20, verbose_name="Код раздела")
    title = models.CharField(max_length=200, verbose_name="Название раздела")
    content = models.TextField(verbose_name="Содержание")
    external_link = models.URLField(blank=True, verbose_name="Внешняя ссылка")
    attached_file = models.FileField(upload_to='section_files/', blank=True, null=True,
                                     verbose_name="Приложенный файл")  # Новое поле
    image = models.ImageField(upload_to='section_images/', blank=True, null=True, verbose_name="Изображение")
    interactive_data = models.JSONField(blank=True, null=True, verbose_name="Данные для интерактивного задания")
    order = models.IntegerField(default=0, verbose_name="Порядок")

    class Meta:
        ordering = ['order']
        verbose_name = 'Раздел'
        verbose_name_plural = 'Разделы'

    def __str__(self):
        return f"{self.code} {self.title}"


# НОВАЯ МОДЕЛЬ ПРОФИЛЯ ПОЛЬЗОВАТЕЛЯ
class UserProfile(models.Model):
    USER_ROLES = [
        ('student', 'Студент'),
        ('teacher', 'Преподаватель'),
        ('admin', 'Администратор'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=USER_ROLES, default='student')
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f"{self.user.username} ({self.role})"


# МОДЕЛЬ ОБРАТНОЙ СВЯЗИ
class Feedback(models.Model):
    FEEDBACK_TYPES = [
        ('bug', 'Ошибка на сайте'),
        ('suggestion', 'Предложение по улучшению'),
        ('content', 'Вопрос по содержанию курса'),
        ('technical', 'Техническая проблема'),
        ('other', 'Другое'),
    ]

    STATUS_CHOICES = [
        ('new', 'Новое'),
        ('in_progress', 'В обработке'),
        ('resolved', 'Решено'),
        ('closed', 'Закрыто'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES, default='suggestion')
    subject = models.CharField(max_length=200, verbose_name="Тема")
    message = models.TextField(verbose_name="Сообщение")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True, null=True, verbose_name="Заметки администратора")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Связь с контентом курса (опционально)
    module = models.ForeignKey(Module, on_delete=models.SET_NULL, blank=True, null=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name = 'Обратная связь'
        verbose_name_plural = 'Обратная связь'
        ordering = ['-created_at']

    def __str__(self):
        return f"Обратная связь от {self.user.username}: {self.subject}"


# СИГНАЛЫ ДЛЯ АВТОМАТИЧЕСКОГО СОЗДАНИЯ ПРОФИЛЯ
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()