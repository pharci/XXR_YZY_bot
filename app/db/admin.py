from typing import List, Optional
from pydantic import BaseModel

class AdminField(BaseModel):
    name: str
    display_name: Optional[str] = None
    editable: bool = False
    required: bool = False
    related_model: Optional[str] = None

class AdminModel(BaseModel):
    model_name: str
    fields: List[AdminField]
    display_fields: List[str]  # Список полей для отображения на странице списка
    detail_fields: List[str]  # Список полей для отображения на странице деталей
    related_fields: List[str]

# Пример использования модели:
admin_models = {
    "users": AdminModel(
        model_name="users",
        fields=[
            AdminField(name="id", display_name="id", editable=False),
            AdminField(name="user_id", display_name="Telegram ID", editable=False),
            AdminField(name="username", display_name="Никнейм", editable=False),
            AdminField(name="first_name", display_name="Имя", editable=False),
            AdminField(name="description", display_name="Описание", editable=True),
            AdminField(name="date_created", display_name="Дата регистрации", editable=False),
        ],
        display_fields=["id", "username", "date_created"],
        detail_fields=["id", "user_id", "username", "first_name", "description", "date_created"],
        related_fields=[],
    ),
    "orders": AdminModel(
        model_name="orders",
        fields=[
            AdminField(name="id", display_name="id", editable=False),
            AdminField(name="order_id", display_name="Номер заказа", editable=False),
            AdminField(name="user", display_name="Пользователь", editable=False, related_model="users"),
            AdminField(name="contact_method", display_name="Метод связи", editable=True),
            AdminField(name="amount", display_name="Сумма", editable=True),
            AdminField(name="currency", display_name="Валюта пользователя", editable=False),
            AdminField(name="exchange_currency", display_name="Валюта для получения", editable=False),
            AdminField(name="exchange_rate", display_name="Курс", editable=True),
            AdminField(name="date_created", display_name="Дата создания", editable=False),
        ],
        display_fields=["id", "order_id", "contact_method"],
        detail_fields=["id", "order_id", "user", "amount", "currency", "exchange_currency", "exchange_rate", "contact_method", "date_created"],
        related_fields=["user"],
    ),
    "sysdata": AdminModel(
        model_name="sysdata",
        fields=[
            AdminField(name="id", display_name="id", editable=False),
            AdminField(name="currency", display_name="Валюта пользователя", editable=True),
            AdminField(name="exchange_currency", display_name="Пользователь получит", editable=True, related_model="users"),
            AdminField(name="exchange_rate", display_name="Курс", editable=True),
            AdminField(name="graduation_step", display_name="Градация", editable=True),
        ],
        display_fields=["id", "currency", "exchange_currency"],
        detail_fields=["id", "currency", "exchange_currency", "exchange_rate", "graduation_step"],
        related_fields=[],
    ),
}