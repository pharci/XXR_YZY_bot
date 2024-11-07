from tortoise import fields, models

class Sysdata(models.Model):
    currency = fields.CharField(max_length=10)  # Валюта
    exchange_currency = fields.CharField(max_length=10)  # Валюта для обмена
    exchange_rate = fields.DecimalField(max_digits=10, decimal_places=4)  # Курс
    graduation_step = fields.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        table = "sysdata"

class PromoCode(models.Model):
    code = fields.CharField(max_length=50, unique=True)  # Код промокода
    discount_type = fields.CharField(max_length=20)  # Тип скидки (например: "обучение", "конвертация")
    one_time = fields.BooleanField(default=False)  # Одноразовый
    multiple_use = fields.BooleanField(default=False)  # Многоразовый
    eternal = fields.BooleanField(default=False)  # Вечный
    max_activations = fields.IntField(default=1)  # Количество активаций
    activations_count = fields.IntField(default=0)  # Текущее количество активаций

    class Meta:
        table = "promocodes"