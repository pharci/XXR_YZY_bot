from pydantic import BaseModel, Field

class ConversionGet(BaseModel):
    currency: str = Field(..., max_length=10)
    exchange_currency: str = Field(..., max_length=10)
    exchange_rate: float
    graduation_step: float