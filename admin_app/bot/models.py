from django.db import models

class Bot(models.Model):
    message_id = models.IntegerField('Айди сообщения в боте', unique=True)
    name = models.CharField('Название', max_length=100)
    text = models.TextField('Текст', max_length=2048)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Сообщение бота"
        verbose_name_plural = "Сообщения бота"

    def __str__(self):
        return self.name
