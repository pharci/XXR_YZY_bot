from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from typing import Optional
from datetime import datetime
from app.db.models.user import User
from app.db.models.order import OrderStatus

class OrderCreate(BaseModel):
    user: User
    contact_method: str
    currency: str = Field(..., max_length=10)
    amount: Decimal
    exchange_currency: str = Field(..., max_length=10)
    exchange_rate: Decimal

    model_config = ConfigDict(arbitrary_types_allowed=True)

class OrderGet(BaseModel):
    order_id: int
    contact_method: Optional[str] = None
    currency: str = Field(..., max_length=10)
    amount: Decimal
    status: OrderStatus
    exchange_currency: str = Field(..., max_length=10)
    exchange_rate: Decimal
    date_created: datetime

    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True