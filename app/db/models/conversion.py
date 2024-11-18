from tortoise.models import Model
from tortoise import fields

class Graduations(Model):
    id = fields.IntField(pk=True)
    min_amount = fields.DecimalField(max_digits=10, decimal_places=2)
    max_amount = fields.DecimalField(max_digits=10, decimal_places=2)
    adjustment = fields.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        table = "graduations"
        table_description = "Градация"

    def __str__(self):
        return f"{self.adjustment}: {self.min_amount} - {self.max_amount}"

class Conversion(Model):
    id = fields.IntField(pk=True)
    user_currency = fields.CharField(max_length=10)
    exchange_currency = fields.CharField(max_length=10)
    course = fields.DecimalField(max_digits=10, decimal_places=2)
    clean_course = fields.DecimalField(max_digits=10, decimal_places=2)
    graduations = fields.ManyToManyField("models.Graduations", related_name="conversions", null=True)
    updated_at = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "conversions"
        table_description = "Конвертация"

    def __str__(self):
        return f"{self.user_currency} -> {self.exchange_currency}"