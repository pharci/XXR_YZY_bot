from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from typing import Optional
from datetime import datetime
from app.db.models.user import User

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
    exchange_currency: str = Field(..., max_length=10)
    exchange_rate: Decimal
    date_created: datetime

    model_config = ConfigDict(arbitrary_types_allowed=True)