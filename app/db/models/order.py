from tortoise import fields, models

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