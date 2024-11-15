from typing import List, Optional
from pydantic import BaseModel
from enum import Enum

class OrderStatus(str, Enum):
    CREATING = "Создан"
    PROCESSING = "В обработке"
    COMPLETED = "Выполнен"
    CANCELED = "Отменен"

class AdminField(BaseModel):
    name: str
    display_name: Optional[str] = None
    editable: bool = False
    required: bool = False
    related_model: Optional[str] = None
    type: Optional[str] = None
    text: Optional[str] = ""
    choices: Optional[List[str]] = []

class AdminModel(BaseModel):
    model_name: str
    fields: List[AdminField]
    display_fields: List[str]
    detail_fields: List[str]
    related_fields: List[str]
    create_records: bool = False
    filter: str = None
    filter_btn: str = None

admin_models = {
    "users": AdminModel(
        model_name="users",
        fields=[
            AdminField(name="id", display_name="id", editable=False),
            AdminField(name="user_id", display_name="Telegram ID", editable=False),
            AdminField(name="username", display_name="Никнейм", editable=False),
            AdminField(name="first_name", display_name="Имя", editable=False),
            AdminField(name="description", display_name="Описание", editable=True, text="Поле для заметок"),
            AdminField(name="is_staff", display_name="Персонал", editable=True, type="bool"),
            AdminField(name="is_superuser", display_name="Суперюзер", editable=True, type="bool"),
            AdminField(name="date_created", display_name="Дата регистрации", editable=False, type="date"),
        ],
        display_fields=["id", "user_id", "username"],
        detail_fields=["id", "user_id", "username", "first_name", "is_staff", "is_superuser", "description", "date_created"],
        related_fields=[],
        filter="user_id",
    ),
    "orders": AdminModel(
        model_name="orders",
        fields=[
            AdminField(name="id", display_name="id", editable=False),
            AdminField(name="order_id", display_name="Номер заказа", editable=False),
            AdminField(name="user", display_name="Пользователь", editable=False, related_model="users"),
            AdminField(name="status", display_name="Статус", editable=True, type="select", text="Choose status", choices=[status.value for status in OrderStatus]),
            AdminField(name="contact_method", display_name="Метод связи", editable=True, text="Номер, почта"),
            AdminField(name="amount", display_name="Сумма", editable=True, text="10000"),
            AdminField(name="currency", display_name="Валюта пользователя", editable=False),
            AdminField(name="exchange_currency", display_name="Валюта для получения", editable=False),
            AdminField(name="exchange_rate", display_name="Курс", editable=True, text="14.5"),
            AdminField(name="date_created", display_name="Дата создания", editable=False, type="date"),
        ],
        display_fields=["id", "order_id", "status"],
        detail_fields=["id", "order_id", "user", "status", "amount", "currency", "exchange_currency", "exchange_rate", "contact_method", "date_created"],
        related_fields=["user"],
        filter="order_id",
        filter_btn="status",
    ),
    "sysdata": AdminModel(
        model_name="sysdata",
        fields=[
            AdminField(name="id", display_name="id", editable=False),
            AdminField(name="currency", display_name="Валюта пользователя", editable=True, text="USD"),
            AdminField(name="exchange_currency", display_name="Пользователь получит", editable=True, related_model="users", text="CNY"),
            AdminField(name="exchange_rate", display_name="Курс", editable=True, text="13.9"),
            AdminField(name="graduation_step", display_name="Градация", editable=True, text="0.1"),
        ],
        display_fields=["id", "currency", "exchange_currency"],
        detail_fields=["id", "currency", "exchange_currency", "exchange_rate", "graduation_step"],
        related_fields=[],
        create_records=True,
    ),
    "promocode": AdminModel(
        model_name="promocode",
        fields=[
            AdminField(name="id", display_name="id", editable=False),
            AdminField(name="code", display_name="Код промокода", editable=True, text="SUMMER2024"),
            AdminField(name="study", display_name="Обучение", editable=True, type="bool", text="Если скидка на обучение, иначе конвертация"),
            AdminField(name="one_time", display_name="Одноразовый", editable=True, type="bool"),
            AdminField(name="multiple_use", display_name="Многоразовый", editable=True, type="bool"),
            AdminField(name="eternal", display_name="Вечный", editable=True, type="bool"),
            AdminField(name="max_activations", display_name="Количество активаций", editable=True, text="1000"),
            AdminField(name="activations_count", display_name="Текущее количество активаций", editable=False),
        ],
        display_fields=["id", "code", "activations_count"],
        detail_fields=["id", "code", "study", "one_time", "multiple_use", "eternal", "max_activations", "activations_count"],
        related_fields=[],
        create_records=True,
        filter="code",
    ),
}