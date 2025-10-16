from django.db import models


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