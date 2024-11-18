from typing import List, Optional, Literal
from pydantic import BaseModel
from app.db.models.user import User, UserActivity

# class AdminField(BaseModel):
#     name: str
#     display_name: Optional[str] = None
#     editable: bool = False
#     related_model: Optional[str] = None
#     multiple: bool = False

# class AdminModel(BaseModel):
#     model_name: str
#     fields: List[AdminField]
#     display_fields: List[str]
#     detail_fields: List[str]
#     related_fields: List[str] = [] 
#     create_records: bool = False
#     text_filter: Optional[str] = None
#     select_filter: Optional[List[str]] = None
#     date_filter: Optional[str] = None



class AdminRegistry:
    def __init__(self):
        self._registry = {}

    def register(self, model, admin_class):
        self._registry[model] = admin_class()

    def get_admin_class(self, model):
        return self._registry.get(model)

class AdminField(BaseModel):
    name: str
    display_name: Optional[str]

    class Config:
        arbitrary_types_allowed = True

class InlineModel:
    model: BaseModel
    extra: int = 1
    fields: List[AdminField]
    verbose_name: Optional[str]
    verbose_name_plural: Optional[str]

    class Config:
        arbitrary_types_allowed = True

class AdminModel(BaseModel):
    model: Optional[str]
    fields: List[AdminField] #поля при редактировании
    list_display: List[AdminField] #отображение в списке записей
    list_filter: List[AdminField] #фильтры-списки
    search_fields: List[AdminField] #по каким полям искать в строке поиска
    readonly_fields: List[AdminField] #поля только для чтения
    inlines: List[InlineModel] #связанные модели
    verbose_name: Optional[str] #имя в единственном числе
    verbose_name_plural: Optional[str] #имя во множественном числе

    class Config:
        arbitrary_types_allowed = True

class UserActivityAdmin(InlineModel):
    extra: int = 0
    fields: List[AdminField] = [
        AdminField(name="activity_type", display_name="Тип"),
        AdminField(name="created_at", display_name="Время"),
    ]
    verbose_name: Optional[str] = "Активность"
    verbose_name_plural: Optional[str] = "Активности"

class UserAdmin(AdminModel):
    model: Optional[str] = "user"
    fields: List[AdminField] = [
        AdminField(name="username", display_name="Никнейм"),
        AdminField(name="user_id", display_name="Телеграм ID"),
        AdminField(name="first_name", display_name="Имя"),
        AdminField(name="description", display_name="Заметки"),
        AdminField(name="updated_at", display_name="Последнее обновление"),
        AdminField(name="created_at", display_name="Дата регистрации"),
    ]
    list_display: List[AdminField] = [
        AdminField(name="username", display_name="Никнейм"),
        AdminField(name="created_at", display_name="Дата регистрации"),
    ]
    list_filter: List[AdminField] = [
        AdminField(name="created_at", display_name="Дата регистрации"),
    ]
    search_fields: List[AdminField] = [
        AdminField(name="username", display_name="Никнейм"),
    ]
    readonly_fields: List[AdminField] = [
        AdminField(name="username", display_name="Никнейм"),
        AdminField(name="user_id", display_name="Телеграм ID"),
    ]
    inlines: List[AdminField] = [UserActivityAdmin]
    verbose_name: Optional[str] = "Пользователь"
    verbose_name_plural: Optional[str] = "Пользователи"

admin_registry = AdminRegistry()
admin_registry.register(User, UserAdmin)



# admin_models = {
#     "User": AdminModel(
#         model_name="User",
#         fields=[
#             AdminField(name="id", display_name="ID", editable=False),
#             AdminField(name="username", display_name="Никнейм", editable=True),
#             AdminField(name="user_id", display_name="Телеграм ID", editable=True),
#             AdminField(name="first_name", display_name="Имя", editable=True),
#             AdminField(name="description", display_name="Заметки", editable=True),
#             AdminField(name="updated_at", display_name="Последнее обновление", editable=True),
#             AdminField(name="created_at", display_name="Дата регистрации", editable=True),
#         ],
#         display_fields=["id", "username", "created_at"],
#         detail_fields=["id", "username", "user_id", "first_name", "description", "updated_at", "created_at"],
#         text_filter="username",
#         date_filter="created_at"
#     ),
#     "UserActivity": AdminModel(
#         model_name="UserActivity",
#         fields=[
#             AdminField(name="id", display_name="ID", editable=False),
#             AdminField(name="user", display_name="Пользователь", editable=True, related_model="User"),
#             AdminField(name="activity_type", display_name="Тип", editable=True),
#             AdminField(name="device", display_name="Устройство", editable=True),
#             AdminField(name="ip_address", display_name="IP Adress", editable=True),
#             AdminField(name="created_at", display_name="Время", editable=True),
#         ],
#         display_fields=["id", "user", "activity_type", "created_at"],
#         detail_fields=["id", "user", "activity_type", "device", "ip_address", "created_at"],
#         related_fields=["user"],
#     ),
#     "Role": AdminModel(
#         model_name="Role",
#         fields=[
#             AdminField(name="id", display_name="ID", editable=False),
#             AdminField(name="name", display_name="Название", editable=True),
#             AdminField(name="can_create", display_name="Создание", editable=True),
#             AdminField(name="can_edit", display_name="Редактирование", editable=True),
#             AdminField(name="can_delete", display_name="Удаление", editable=True),
#             AdminField(name="can_view", display_name="Просмотр", editable=True),
#         ],
#         display_fields=["id", "name"],
#         detail_fields=["id", "name", "can_create", "can_edit", "can_delete", "can_view"],
#         create_records=True,
#     ),
#     "UserRole": AdminModel(
#         model_name="UserRole",
#         fields=[
#             AdminField(name="id", display_name="ID", editable=False),
#             AdminField(name="user", display_name="Пользователь", editable=True, related_model="User"),
#             AdminField(name="role", display_name="Роль", editable=True, related_model="Role"),
#             AdminField(name="created_at", display_name="Дата назначения", editable=False),
#         ],
#         display_fields=["id", "user", "role", "created_at"],
#         detail_fields=["id", "user", "role", "created_at"],
#         related_fields=["user", "role"],
#         create_records=True,
#     ),
#     "Order": AdminModel(
#         model_name="Order",
#         fields=[
#             AdminField(name="id", display_name="ID", editable=False),
#             AdminField(name="user", display_name="Пользователь", editable=False, related_model="User"),
#             AdminField(name="order_id", display_name="Номер заказа", editable=True),
#             AdminField(name="status", display_name="Статус", editable=True, related_model="OrderStatus"),
#             AdminField(name="type", display_name="Тип заказа", editable=True),
#             AdminField(name="contact_method", display_name="Способ связи", editable=True),
#             AdminField(name="amount", display_name="Сумма", editable=True),
#             AdminField(name="conversion", display_name="Конвертация", editable=True, related_model="Conversion"),
#             AdminField(name="exchange_rate", display_name="Курс", editable=True),
#             AdminField(name="promocode", display_name="Промокод", editable=True, related_model="Promocode"),
#             AdminField(name="updated_at", display_name="Последнее обновление", editable=True),
#             AdminField(name="created_at", display_name="Дата оформления", editable=True),
#         ],
#         display_fields=["id", "order_id", "status", "type", "created_at"],
#         detail_fields=["id", "user", "order_id", "status", "type", "contact_method", "amount", "conversion", "exchange_rate", "promocode", "updated_at", "created_at"],
#         related_fields=["user", "status", "conversion", "promocode"],
#         date_filter="created_at"
#     ),
#     "OrderStatus": AdminModel(
#         model_name="OrderStatus",
#         fields=[
#             AdminField(name="id", display_name="ID", editable=False),
#             AdminField(name="name", display_name="Название статуса", editable=True),
#             AdminField(name="description", display_name="Описание статуса", editable=True),
#         ],
#         display_fields=["id", "name", "description"],
#         detail_fields=["id", "name", "description"],
#         create_records=True,
#     ),
#     "OrderType": AdminModel(
#         model_name="OrderType",
#         fields=[
#             AdminField(name="id", display_name="ID", editable=False),
#             AdminField(name="name", display_name="Название типа", editable=True),
#             AdminField(name="description", display_name="Описание типа", editable=True),
#         ],
#         display_fields=["id", "name", "description"],
#         detail_fields=["id", "name", "description"],
#         create_records=True,
#     ),
#     "Promocode": AdminModel(
#         model_name="Promocode",
#         fields=[
#             AdminField(name="id", display_name="ID", editable=False),
#             AdminField(name="user", display_name="Для пользователя", editable=True, related_model="User"),
#             AdminField(name="code", display_name="Код", editable=True),
#             AdminField(name="order_type", display_name="Тип заказа", editable=True, related_model="OrderType"),
#             AdminField(name="discount", display_name="Сумма скидки", editable=True),
#             AdminField(name="percent", display_name="В процентах?", editable=True),
#             AdminField(name="activations", display_name="Активации", editable=True),
#             AdminField(name="max_activations", display_name="Всего активаций", editable=True),
#             AdminField(name="one_time", display_name="Одноразовый?", editable=True),
#             AdminField(name="start_at", display_name="Действует с", editable=True),
#             AdminField(name="end_at", display_name="Действует до", editable=True),
#             AdminField(name="updated_at", display_name="Последнее обнволение", editable=True),
#             AdminField(name="created_at", display_name="Дата создания", editable=True),
#         ],
#         display_fields=["id", "code"],
#         detail_fields=["id", "user", "code", "order_type", "discount", "percent", "activations", "max_activations", "one_time", "start_at", "end_at", "updated_at", "created_at"],
#         create_records=True,
#         related_fields=["user", "order_type"],
#     ),
#     "PromocodeUsage": AdminModel(
#         model_name="PromocodeUsage",
#         fields=[
#             AdminField(name="id", display_name="ID", editable=False),
#             AdminField(name="promocode", display_name="Промокод", editable=True, related_model="Promocode"),
#             AdminField(name="user", display_name="Пользователь", editable=True, related_model="User"),
#             AdminField(name="created_at", display_name="Время использования", editable=True),
#         ],
#         display_fields=["id", "promocode", "user", "created_at"],
#         detail_fields=["id", "promocode", "user", "created_at"],
#         related_fields=["promocode", "user"],
#     ),
#     "Conversion": AdminModel(
#         model_name="Conversion",
#         fields=[
#             AdminField(name="id", display_name="ID", editable=False),
#             AdminField(name="user_currency", display_name="Валюта пользователя", editable=True),
#             AdminField(name="exchange_currency", display_name="Пользователь получит", editable=True),
#             AdminField(name="course", display_name="Курс", editable=True),
#             AdminField(name="clean_course", display_name="Чистый курс", editable=True),
#             AdminField(name="graduations", display_name="Градация", editable=True, related_model="Graduations", multiple=True),
#         ],
#         display_fields=["id", "user_currency", "exchange_currency", "course"],
#         detail_fields=["id", "user_currency", "exchange_currency", "course", "clean_course", "graduations"],
#         related_fields=["graduations"],
#         create_records=True,
#     ),
#     "Graduations": AdminModel(
#         model_name="Graduations",
#         fields=[
#             AdminField(name="id", display_name="ID", editable=False),
#             AdminField(name="min_amount", display_name="От", editable=True),
#             AdminField(name="max_amount", display_name="До", editable=True),
#             AdminField(name="adjustment", display_name="Значение", editable=True),
#         ],
#         display_fields=["id", "min_amount", "max_amount", "adjustment"],
#         detail_fields=["id", "min_amount", "max_amount", "adjustment"],
#         create_records=True,
#     ),
# }