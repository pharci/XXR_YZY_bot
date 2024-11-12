from tortoise import fields, models
from pytz import timezone

class Order(models.Model):
    user = fields.ForeignKeyField("models.User", related_name='orders', on_delete=fields.CASCADE)
    order_id = fields.IntField()
    contact_method = fields.CharField(max_length=255, null=True)
    currency = fields.CharField(max_length=10, default="Rub") 
    amount = fields.DecimalField(max_digits=10, decimal_places=2) 
    exchange_currency = fields.CharField(max_length=10)
    exchange_rate = fields.DecimalField(max_digits=10, decimal_places=4)
    date_created = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "orders"

    def date_of_created(self):
        # Установим московское время
        moscow_tz = timezone("Europe/Moscow")
        
        # Переведём дату в московское время и отформатируем
        dt_moscow = self.date_created.astimezone(moscow_tz)
        return dt_moscow.strftime("%d.%m.%Y %H:%M")