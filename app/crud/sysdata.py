from app.db.models.sysdata import Sysdata, PromoCode
from app.schemas.sysdata import SysdataCreate
from typing import List

async def create_currency(sys_data: SysdataCreate) -> Sysdata:
    sysdata = await Sysdata.create(
        currency=sys_data.currency,
        exchange_currency=sys_data.exchange_currency,
        exchange_rate=sys_data.exchange_rate,
        graduation_step=sys_data.graduation_step
    )
    return sysdata

async def get_currency_by_id(currency_id: int) -> Sysdata:
    currency_data = await Sysdata.get(id=currency_id)
    return currency_data

async def get_all_currencies() -> List[Sysdata]:
    currencies = await Sysdata.all()
    return currencies