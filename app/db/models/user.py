from tortoise import fields
from tortoise.models import Model

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255, unique=True)
    user_id = fields.BigIntField(unique=True)
    first_name = fields.CharField(max_length=255, null=True, default=None)
    description = fields.CharField(max_length=255, null=True, default=None)
    updated_at = fields.DatetimeField(auto_now=True)
    created_at  = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "users"

    def __str__(self):
        return self.username

class UserActivity(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="activities", on_delete=fields.CASCADE)
    activity_type = fields.CharField(max_length=255)
    device = fields.CharField(max_length=255, null=True)
    ip_address = fields.CharField(max_length=45, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "user_activities"

class Role(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    can_create = fields.BooleanField(default=False)
    can_edit = fields.BooleanField(default=False)
    can_delete = fields.BooleanField(default=False)
    can_view = fields.BooleanField(default=False)

    class Meta:
        table = "roles"
        table_description = "Роли"
    
    def __str__(self):
        return self.name

class UserRole(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="roles", on_delete=fields.CASCADE)
    role = fields.ForeignKeyField("models.Role", related_name="user_roles", on_delete=fields.CASCADE)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "user_roles"
        unique_together = ("user", "role")