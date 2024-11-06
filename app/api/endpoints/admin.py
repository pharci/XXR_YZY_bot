from fastapi import APIRouter
from app.schemas.sysdata import SysdataCreate

router = APIRouter()

@router.post("/sysdata/")
async def create_sysdata(sysdata: SysdataCreate):
    new_sysdata = await Sysdata.create(
        currency=sysdata.currency,
        exchange_currency=sysdata.exchange_currency,
        exchange_rate=sysdata.exchange_rate,
        graduation_step=sysdata.graduation_step
    )
    return {"id": new_sysdata.id, 
            "currency": new_sysdata.currency, 
            "exchange_currency": new_sysdata.exchange_currency, 
            "exchange_rate": new_sysdata.exchange_rate,
            "graduation_step": new_sysdata.graduation_step,
            }

@router.get("/sysdata/")
async def read_sysdata():
    all_sysdata = await Sysdata.all()
    return all_sysdata