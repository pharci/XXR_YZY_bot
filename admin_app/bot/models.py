from django.db import models

class Bot(models.Model):
    message_id = models.IntegerField('ID сообщения в боте', unique=True)
    name = models.CharField('Название', max_length=100)
    text = models.TextField('Текст раздела', max_length=2048)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Сообщение бота"
        verbose_name_plural = "Сообщения бота"

    def __str__(self):
        return self.name


class Study(models.Model):
    name = models.CharField('Текст на кнопке', max_length=100)
    text = models.TextField('Текст сообщения', max_length=2048)
    amount = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    is_active = models.BooleanField('Обучение активно', default=False)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Тариф обучения"
        verbose_name_plural = "Тарифы обучения"

    def __str__(self):
        return self.name