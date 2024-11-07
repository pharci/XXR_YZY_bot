from tortoise import fields, models

class User(models.Model):
    id = fields.IntField(primary_key=True)
    username = fields.CharField(max_length=255, unique=True)
    user_id = fields.IntField(unique=True)
    date_created = fields.DatetimeField(auto_now_add=True)
    date_updated = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"

class UserActivity(models.Model):
    user = fields.ForeignKeyField("models.User", related_name='activities', on_delete=fields.SET_NULL, null=True)
    activity_type = fields.CharField(max_length=255)  # Тип активности
    timestamp = fields.DatetimeField(auto_now_add=True)  # Время активности

    class Meta:
        table = "user_activities"