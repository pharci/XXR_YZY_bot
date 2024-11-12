from fastapi import APIRouter, HTTPException, Depends, Request
from app.schemas.sysdata import SysdataCreate
from app.crud.sysdata import get_currency_by_id, get_all_currencies, create_currency
from app.crud.user import get_all_users

router = APIRouter()

