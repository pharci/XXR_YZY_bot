from tortoise import fields, models

class User(models.Model):
    id = fields.IntField(primary_key=True)
    username = fields.CharField(max_length=255, unique=True)
    user_id = fields.IntField(unique=True)
    date_created = fields.DatetimeField(auto_now_add=True)
    date_updated = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"

class UserActivity(models.Model):
    user = fields.ForeignKeyField("models.User", related_name='activities', on_delete=fields.SET_NULL, null=True)
    activity_type = fields.CharField(max_length=255)  # Тип активности
    timestamp = fields.DatetimeField(auto_now_add=True)  # Время активности

    class Meta:
        table = "user_activities"

class Order(models.Model):
    user = fields.ForeignKeyField("models.User", related_name='orders', on_delete=fields.CASCADE)
    order_id = fields.IntField()  # Идентификатор заказа
    contact_method = fields.CharField(max_length=255, null=True)  # Способ связи
    currency = fields.CharField(max_length=10, default="Rub")  # Валюта
    amount = fields.DecimalField(max_digits=10, decimal_places=2)  # Количество валюты
    exchange_currency = fields.CharField(max_length=10)  # Валюта для обмена
    exchange_rate = fields.DecimalField(max_digits=10, decimal_places=4)  # Курс обмена
    date_created = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "orders"

class Sysdata(models.Model):
    currency = fields.CharField(max_length=10)  # Валюта
    exchange_currency = fields.CharField(max_length=10)  # Валюта для обмена
    exchange_rate = fields.DecimalField(max_digits=10, decimal_places=4)  # Курс

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