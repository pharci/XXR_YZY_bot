from pydantic import BaseModel, validator
from datetime import datetime
from typing import List

class UserCreate(BaseModel):
    user_id: int
    username: str