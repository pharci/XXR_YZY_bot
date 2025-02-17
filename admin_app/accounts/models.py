from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.hashers import make_password

class User(AbstractUser):
    telegram_id = models.CharField('Telegram ID',max_length=12)
    username = models.CharField('Имя пользователя',max_length=30, unique=True)
    contact = models.CharField('Номер телефона',max_length=20)
    avatar = models.ImageField('Аватар',upload_to="avatars/", null=True, blank=True)
    description = models.TextField('Заметка', null=True, blank=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        if self.password and len(self.password) < 128:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    
    def get_orders(self, ):
        from datetime import timedelta

        orders = self.orders.select_related("currency").order_by("-created_at").all()[:10]

        if not orders:
            return None
        
        orders_text = []

        for order in orders:
            orders_text.append(
                f"<b>Заказ №<code>{order.order_id}</code></b>\n"
                f"<b>📝 Дата заказа:</b> {order.created_at + timedelta(hours=3):%d.%m.%Y %H:%M}\n"
                f"<b>🏷️ Статус:</b> {order.get_status_display()}\n"
                f"<b>📦 Тип заказа:</b> {order.get_type_display()}\n"
                f"{f'<b>🛠️ Тариф:</b> {order.tariff.name}\n' if order.tariff else ''}"
                f"<b>💰 Сумма:</b> {round(order.amount, 0)} {order.currency.user_currency if order.currency else ""}\n" \
                f"{f'<b>🔄 Получено:</b> {round(order.amount_output, 0)} {order.currency.exchange_currency}\n' if order.amount_output else ''}"
                f"{f'<b>📊 Курс обмена:</b> {order.exchange_course} { f"<s>{order.exchange_course + order.promocode.discount}</s>" if order.promocode else ""}\n' if order.exchange_course else ''}"
                f"<b>🎟️ Промокод:</b> {order.promocode.code if order.promocode else 'Нет'}\n"
            )
        return orders_text
        

    
class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class UserActivity(TimestampMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities", verbose_name='Пользователь')
    activity_type = models.CharField('Тип активности', max_length=255)
    device = models.CharField('Устройство', max_length=255, null=True, blank=True)
    ip_address = models.GenericIPAddressField('IP Adress', null=True, blank=True)

    class Meta:
            verbose_name = "Активность пользователя"
            verbose_name_plural = "Активности пользователей"

    def __str__(self):
        return f"{self.user} - {self.activity_type}"
