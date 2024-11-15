from tortoise import fields, models

class Sysdata(models.Model):
    currency = fields.CharField(max_length=10)
    exchange_currency = fields.CharField(max_length=10)
    exchange_rate = fields.DecimalField(max_digits=10, decimal_places=4)
    graduation_step = fields.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        table = "sysdata"

class Promoсode(models.Model):
    code = fields.CharField(max_length=50, unique=True)
    study = fields.BooleanField(default=False)
    one_time = fields.BooleanField(default=False)
    multiple_use = fields.BooleanField(default=False)
    eternal = fields.BooleanField(default=False)
    max_activations = fields.IntField(default=1)
    activations_count = fields.IntField(default=0)

    class Meta:
        table = "promocodes"