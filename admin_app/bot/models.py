from django.db import models
from django_jsonform.models.fields import JSONField

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
    

class Category(models.Model):
    name = models.CharField('Имя категории', max_length=100)
    text = models.TextField('Текст сообщения', max_length=2048)
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Обучение активно', default=False)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

class Tariff(models.Model):
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL, related_name="tariff", verbose_name="Категория")
    name = models.CharField('Текст на кнопке', max_length=100)
    text = models.TextField('Текст сообщения', max_length=2048)
    order = models.PositiveIntegerField('Порядок', default=0)
    amount = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    is_active = models.BooleanField('Обучение активно', default=False)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Тариф обучения"
        verbose_name_plural = "Тарифы обучения"

    def __str__(self):
        return f"{self.category} | {self.name}"