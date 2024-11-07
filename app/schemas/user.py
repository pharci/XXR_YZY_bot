from pydantic import BaseModel
from datetime import datetime
from typing import List

class UserCreate(BaseModel):
    user_id: int
    username: str

class UserGet(BaseModel):
    user_id: int
    username: str
    date_created: datetime