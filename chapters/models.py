from django.db import models


class Chapter(models.Model):
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
    order = models.IntegerField(default=0, verbose_name="Порядок")

    class Meta:
        ordering = ['order']
        verbose_name = 'Раздел'
        verbose_name_plural = 'Разделы'

    def __str__(self):
        return f"{self.code} {self.title}"