from pydantic import BaseModel

class SysdataCreate(BaseModel):
    currency: str
    exchange_currency: str
    exchange_rate: float
    graduation_step: float