from tortoise import fields, models

class User(models.Model):
    id = fields.IntField(primary_key=True)
    username = fields.CharField(max_length=255, unique=True)
    user_id = fields.IntField(unique=True)
    date_created = fields.DatetimeField(auto_now_add=True)
    date_updated = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"