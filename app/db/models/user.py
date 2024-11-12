from tortoise import fields, models
from pytz import timezone

class User(models.Model):
    id = fields.IntField(primary_key=True)
    username = fields.CharField(max_length=255, unique=True)
    user_id = fields.IntField(unique=True)
    first_name = fields.CharField(max_length=255, null=True, default=None)
    description = fields.CharField(max_length=255, null=True, default=None)
    date_created = fields.DatetimeField(auto_now_add=True)
    date_updated = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"

    def date_of_reg(self):
        # Установим московское время
        moscow_tz = timezone("Europe/Moscow")
        
        # Переведём дату в московское время и отформатируем
        dt_moscow = self.date_created.astimezone(moscow_tz)
        return dt_moscow.strftime("%d.%m.%Y %H:%M")

class UserActivity(models.Model):
    user = fields.ForeignKeyField("models.User", related_name='activities', on_delete=fields.SET_NULL, null=True)
    activity_type = fields.CharField(max_length=255)  # Тип активности
    timestamp = fields.DatetimeField(auto_now_add=True)  # Время активности

    class Meta:
        table = "user_activities"