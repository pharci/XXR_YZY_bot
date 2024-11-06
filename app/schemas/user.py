from pydantic import BaseModel, validator
from datetime import datetime
from typing import List

class UserCreate(BaseModel):
    user_id: int
    username: str

class UserGet(BaseModel):
    user_id: int
    username: str
    date_created: datetime

    @validator("date_created", pre=True, always=True)
    def format_date_created(cls, v):
        return v.strftime("%Y-%m-%d %H:%M:%S") if isinstance(v, datetime) else v