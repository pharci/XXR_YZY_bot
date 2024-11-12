from pydantic import BaseModel
from datetime import datetime
from typing import List

class UserCreate(BaseModel):
    user_id: int
    username: str
    first_name: str

class UserGet(BaseModel):
    user_id: int
    username: str
    first_name: str
    description: str
    date_created: datetime