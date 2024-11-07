from fastapi import APIRouter, HTTPException
from app.schemas.sysdata import SysdataCreate
from app.crud.sysdata import get_currency_by_id, get_all_currencies, create_currency

router = APIRouter()

@router.post("/sysdata/")
async def create_currency_ep(sysdata: SysdataCreate):
    return await create_currency(sysdata)

@router.get("/sysdata/")
async def read_sysdata():
    return await get_all_currencies()

@router.get("/sysdata/{currency_id}/")
async def read_currency_by_id(currency_id: int):
    currency = await get_currency_by_id(currency_id)
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    return currency

