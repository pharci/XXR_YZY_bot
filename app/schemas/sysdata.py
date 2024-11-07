from pydantic import BaseModel, Field
from typing import Optional

class SysdataCreate(BaseModel):
    currency: str = Field(..., max_length=10)
    exchange_currency: str = Field(..., max_length=10)
    exchange_rate: float
    graduation_step: float

class SysdataGet(BaseModel):
    currency: str = Field(..., max_length=10)
    exchange_currency: str = Field(..., max_length=10)
    exchange_rate: float
    graduation_step: float