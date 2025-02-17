from django.db import models
from enum import Enum
from admin_app.bot.models import Tariff
from datetime import timedelta
from django_jsonform.models.fields import JSONField

class OrderTypeEnum(Enum):
    STUDY = "study", "Обучение"
    EXCHANGE = "exchange", "Обмен"
    SAFEPAY = "safepay", "Самовыкуп"

    @classmethod
    def choices(cls):
        return [(item.value[0], item.value[1]) for item in cls]

class Conversion(models.Model):
    ITEMS_SCHEMA = {
        'type': 'dict',
        'keys': {
        },
        'additionalProperties': { 'type': 'number' }
    }

    user_currency = models.CharField("Валюта пользователя", max_length=10)
    exchange_currency = models.CharField("Валюта получения", max_length=10)
    course = models.DecimalField("Курс", max_digits=10, decimal_places=2)
    clean_course = models.DecimalField("Чистый курс", max_digits=10, decimal_places=2)
    grades = JSONField("Градация", schema=ITEMS_SCHEMA)
    enabled = models.BooleanField('Отображать в списке',default=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Изменено", auto_now=True)

    class Meta:
        verbose_name = "Валютная пара"
        verbose_name_plural = "Валютные пары"

    def __str__(self):
        return f"{self.user_currency} -> {self.exchange_currency}"


class Promocode(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="promocodes", verbose_name="Для пользователя")
    code = models.CharField('Код', max_length=50, unique=True)
    order_type = models.CharField("Тип заказа", max_length=20, choices=OrderTypeEnum.choices())
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, null=True, blank=True, related_name="promocodes", verbose_name="Тариф обучения")
    conversion = models.ForeignKey(Conversion, on_delete=models.CASCADE, related_name="promocodes", verbose_name="Валютная пара", null=True, blank=True)
    discount = models.DecimalField('Скидка', max_digits=10, decimal_places=2)
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
    
    def increase_activation(self):
        """Увеличивает количество активаций на 1, если не превышен лимит."""
        if self.activations < self.max_activations:
            self.activations += 1
            self.save()
            return True  # Успешно увеличено
        return False  # Лимит активаций превышен
    
    def get_conversion(self):
        return self.conversion
    
    def get_user(self):
        return self.user
    
    def get_tariff(self):
        return self.tariff


class Order(models.Model):
    class OrderStatusChoices(models.TextChoices):
        CREATE = "create", "Создан🆕"
        PENDING = "pending", "Ожидание⏳"
        SHIPPED = "shipped", "Отправлен📦"
        CANCELED = "canceled", "Отменен❌"
        COMPLETED = "completed", "Завершен✅"

    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, null=True, related_name="orders", verbose_name="Пользователь")
    order_id = models.PositiveIntegerField('Номер заказа', unique=True, db_index=True)
    
    type = models.CharField(
        "Тип заказа",
        max_length=20,
        choices=OrderTypeEnum.choices()
    )
    
    status = models.CharField(
        "Статус заказа", 
        max_length=20, 
        choices=OrderStatusChoices.choices, 
        default=OrderStatusChoices.CREATE
    )
    contact = models.CharField('Номер телефона', max_length=20)
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders", verbose_name="Тариф обучения")
    currency = models.ForeignKey("Conversion", on_delete=models.SET_NULL, null=True, blank=True, related_name="orders", verbose_name="Валютная пара")
    amount = models.DecimalField('Пользователь заплатит', max_digits=10, decimal_places=2)
    amount_output = models.DecimalField('Пользователь получит', max_digits=10, decimal_places=2, null=True, blank=True)
    exchange_course = models.DecimalField('Курс обмена', max_digits=10, decimal_places=2, null=True, blank=True)
    clean_course = models.DecimalField('Чистый курс', max_digits=10, decimal_places=2, null=True, blank=True)
    profit = models.DecimalField('Прибыль', max_digits=10, decimal_places=2, null=True, blank=True)
    promocode = models.ForeignKey(Promocode, on_delete=models.CASCADE, related_name="orders", verbose_name="Промокод", null=True, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата последнего изменения', auto_now=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        permissions = [
            ('can_export_data', 'Может экспортировать заказы'),
            ('can_view_clean_course', 'Может смотреть чистый курс'),
            ('can_view_receive', 'Может смотреть прибыль'),
        ]

    def __str__(self):
        return f"Заказ {self.order_id} ({self.get_type_display()} - {self.get_status_display()})"
    
    def get_text(self):
        text = f"<b>Заказ №<code>{self.order_id}</code></b>\n" \
            f"<b>📝 Дата заказа:</b> {self.created_at + timedelta(hours=3):%d.%m.%Y %H:%M}\n" \
            f"<b>🏷️ Статус:</b> {self.get_status_display()}\n" \
            f"<b>📦 Тип заказа:</b> {self.get_type_display()}\n" \
            f"{f'<b>🛠️ Тариф:</b> {self.tariff.name}\n' if self.tariff else ''}" \
            f"<b>💰 Сумма:</b> {round(self.amount, 0)} {self.currency.user_currency if self.currency else ""}\n" \
            f"{f'<b>🔄 Получено:</b> {round(self.amount_output, 0)} {self.currency.exchange_currency}\n' if self.amount_output else ''}" \
            f"{f'<b>📊 Курс обмена:</b> {self.exchange_course}\n' if self.exchange_course else ''}" \
            f"<b>🎟️ Промокод:</b> {self.promocode.code if self.promocode else 'Нет'}\n"
        
        return text 
    
    def save(self, *args, **kwargs):
        if self.amount is not None and self.amount_output is not None and self.clean_course is not None:
            self.profit = round((self.amount / self.clean_course - self.amount_output) * self.clean_course, 2)
        super().save(*args, **kwargs)


