from django.db import models
from decimal import Decimal

class Graduation(models.Model):
    amount = models.DecimalField("Сумма от", max_digits=10, decimal_places=2)
    adjustment = models.DecimalField("Отнимается от курса", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Градация"
        verbose_name_plural = "Градации"

    def __str__(self):
        return f"От {self.amount}: -{self.adjustment}"


class Conversion(models.Model):
    user_currency = models.CharField("Валюта пользователя", max_length=10)
    exchange_currency = models.CharField("Валюта получения", max_length=10)
    course = models.DecimalField("Курс", max_digits=10, decimal_places=2)
    clean_course = models.DecimalField("Чистый курс", max_digits=10, decimal_places=2)
    graduations = models.ManyToManyField(Graduation, related_name="conversions", verbose_name="Градация")
    enabled = models.BooleanField('Отображать в списке',default=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Изменено", auto_now=True)

    class Meta:
        verbose_name = "Конвертация"
        verbose_name_plural = "Конвертации"

    def __str__(self):
        return f"{self.user_currency} -> {self.exchange_currency}"

class OrderType(models.Model):
    name = models.CharField('Тип заказа', max_length=255)
    description = models.TextField('Описание', null=True, blank=True)

    class Meta:
        verbose_name = "Тип заказа"
        verbose_name_plural = "Типы заказа"

    def __str__(self):
        return self.name
        


class OrderStatus(models.Model):
    name = models.CharField('Статус заказа', max_length=255)
    description = models.TextField('Описание', null=True, blank=True)

    class Meta:
        verbose_name = "Статус заказа"
        verbose_name_plural = "Статусы заказа"

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, null=True, related_name="orders", verbose_name="Пользователь")
    order_id = models.PositiveIntegerField('Номер заказа', unique=True, db_index=True)
    status = models.ForeignKey(OrderStatus, on_delete=models.SET_NULL, null=True, related_name="orders", verbose_name="Статус заказа")
    type = models.ForeignKey(OrderType, on_delete=models.SET_NULL, null=True, related_name="orders", verbose_name="Тип заказа")
    contact = models.CharField('Номер телефона',max_length=20)
    currency = models.ForeignKey(Conversion, on_delete=models.SET_NULL, null=True, related_name="orders", verbose_name="Конвертация")
    amount = models.DecimalField('Пользователь заплатит', max_digits=10, decimal_places=2)
    amount_output = models.DecimalField('Пользователь получит', max_digits=10, decimal_places=2)
    exchange_rate = models.DecimalField('По курсу', max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Изменен', auto_now=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Order {self.order_id}"

class Promocode(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="promocodes", verbose_name="Для пользователя")
    code = models.CharField('Код', max_length=50, unique=True)
    order_type = models.ForeignKey(OrderType, on_delete=models.CASCADE, related_name="promocodes", verbose_name="Для типа заказа")
    conversion = models.ForeignKey(Conversion, on_delete=models.CASCADE, related_name="promocodes", verbose_name="Валютная пара")
    discount = models.DecimalField('Скидка (Количество от курса)', max_digits=10, decimal_places=2)
    activations = models.PositiveIntegerField('Активаций сейчас', default=0)
    max_activations = models.PositiveIntegerField('Всего активаций')
    start_at = models.DateTimeField('Можно использовать с',)
    end_at = models.DateTimeField('Можно использовать до',)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Изменен', auto_now=True)

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"

    def __str__(self):
        return self.code


class PromocodeUsage(models.Model):
    promocode = models.ForeignKey(Promocode, on_delete=models.CASCADE, related_name="usages", verbose_name="Промокод")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="promocode_usages", verbose_name="Пользователь")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="promocode_usages", verbose_name="Заказ")
    created_at = models.DateTimeField("Дата активации", auto_now_add=True)

    class Meta:
        verbose_name = "Использование промокода"
        verbose_name_plural = "Использования промокодов"

    def __str__(self):
        return f"{self.promocode.code} - {self.user}"