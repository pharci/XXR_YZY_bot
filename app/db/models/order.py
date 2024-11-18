from tortoise import fields
from tortoise.models import Model
    
class Order(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="orders", on_delete=fields.CASCADE)
    order_id = fields.IntField(unique=True)
    status = fields.ForeignKeyField("models.OrderStatus", related_name="orders")
    type = fields.ForeignKeyField("models.OrderType", related_name="orders")
    contact_method = fields.CharField(max_length=255)
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    conversion = fields.ForeignKeyField("models.Conversion", related_name="orders", null=True)
    exchange_rate = fields.DecimalField(max_digits=10, decimal_places=6, null=True)
    promocode = fields.ForeignKeyField("models.Promocode", related_name="orders", null=True)
    updated_at = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "orders"
        table_description = "Заказы"

    def __str__(self):
        return self.order_id
    
class OrderType(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)

    class Meta:
        table = "order_types"
        table_description = "Типы заказов"

    def __str__(self):
        return self.name

class OrderStatus(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)

    class Meta:
        table = "order_statuses"
        table_description = "Статусы заказов"

    def __str__(self):
        return self.name