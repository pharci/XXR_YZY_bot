from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
from admin_app.orders.models import Order, Promocode
from django.db.models import Sum
import locale

locale.setlocale(locale.LC_TIME, 'ru_RU')

class User(AbstractUser):
    telegram_id = models.CharField('Telegram ID',max_length=12)
    username = models.CharField('Имя пользователя',max_length=30, unique=True)
    contact = models.CharField('Номер телефона',max_length=20)
    description = models.TextField('Заметка', null=True, blank=True)
    percentage_of_profit = models.DecimalField('Процент прибыли работника', max_digits=10, decimal_places=2, null=True, blank=True, default=30)
    get_notifications_orders = models.BooleanField('Получать уведомления о заказах', default=False)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith("pbkdf2_sha256$"):
            self.set_password(self.password)
        super().save(*args, **kwargs)
    
    def get_orders(self, ):
        from datetime import timedelta

        orders = self.orders.select_related("currency").order_by("-created_at").all()[:10]

        if not orders:
            return None
        
        orders_text = []

        for order in orders:
            orders_text.append(order.get_text())
        return orders_text
    
    def get_profit_by_month(self):
        now = timezone.now()
        # Преобразуем дату в начало месяца и конец месяца
        months = []

        for month in range(1, 13):  # Группируем по месяцам с 1 по 12
            start_of_month = now.replace(year=now.year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_of_month = (start_of_month + timedelta(days=32)).replace(day=1)  # Следующий месяц

            # Сумма прибыли за месяц
            total_profit = Order.objects.filter(admin=self, created_at__gte=start_of_month, created_at__lt=end_of_month).aggregate(Sum('admin_profit'))['admin_profit__sum'] or 0
            months.append({
                'month': start_of_month.strftime('%B'),  # Название месяца, например, "Январь"
                'profit': total_profit
            })
        
        return months

class PromocodeUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="promocode_usage", verbose_name='Пользователь')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="promocode_usage", verbose_name='Заказ')
    promocode = models.ForeignKey(Promocode, on_delete=models.CASCADE, related_name="promocode_usage", verbose_name='Промокод')
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
            verbose_name = "Использование промокода"
            verbose_name_plural = "Использования промокодов"

    def __str__(self):
        return f"{self.user} - Промо: {self.promocode.code} - Заказ: {self.order.order_id}"
