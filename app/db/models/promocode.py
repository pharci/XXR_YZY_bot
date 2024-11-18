from tortoise.models import Model
from tortoise import fields
from datetime import datetime

class Promocode(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="promocodes", null=True)
    code = fields.CharField(max_length=50, unique=True)
    order_type = fields.ForeignKeyField("models.OrderType", related_name="promocodes", null=True)
    discount = fields.DecimalField(max_digits=10, decimal_places=2)
    percent = fields.BooleanField(default=False)
    activations = fields.IntField(default=0)
    max_activations = fields.IntField(null=True)
    one_time = fields.BooleanField(default=False)
    start_at = fields.DatetimeField(null=True)
    end_at = fields.DatetimeField(null=True)
    updated_at = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    def is_valid(self):
        now = datetime.now()
        if self.start_date and self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        return True
    
    def activate(self):
        if self.max_activations and self.activations >= self.max_activations:
            raise ValueError("Промокод достиг максимального количества активаций")
        self.activations += 1
        self.save()

    class Meta:
        table = "promocodes"
        table_description = "Промокоды"

    def __str__(self):
        return self.code

class PromocodeUsage(Model):
    id = fields.IntField(pk=True)
    promocode = fields.ForeignKeyField("models.Promocode", related_name="usages")
    user = fields.ForeignKeyField("models.User", related_name="promocode_usages")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "promocode_usages"
        table_description = "Использование промокодов"