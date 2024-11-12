from app.db.models.sysdata import Sysdata, Promoсode
from app.schemas.sysdata import SysdataCreate
from typing import List
from decimal import Decimal

async def create_currency(sys_data: SysdataCreate) -> Sysdata:
    sysdata = await Sysdata.create(
        currency=sys_data.currency,
        exchange_currency=sys_data.exchange_currency,
        exchange_rate=sys_data.exchange_rate,
        graduation_step=sys_data.graduation_step
    )
    return sysdata

async def get_currency_by_id(sysdata_id: int) -> Sysdata:
    currency_data = await Sysdata.get(id=sysdata_id)
    return currency_data

async def get_all_currencies() -> List[Sysdata]:
    currencies = await Sysdata.all()
    return currencies

async def update_currency(sysdata_id: int, currency: str = None, exchange_currency: str = None, exchange_rate: Decimal = None, graduation_step: Decimal = None):
    sysdata = await get_currency_by_id(sysdata_id)
    if sysdata:
        update_fields = []
        if currency:
            sysdata.currency = currency
            update_fields.append('currency')
        if exchange_currency:
            sysdata.exchange_currency = exchange_currency
            update_fields.append('exchange_currency')
        if exchange_rate:
            sysdata.exchange_rate = exchange_rate
            update_fields.append('exchange_rate')
        if graduation_step:
            sysdata.graduation_step = graduation_step
            update_fields.append('graduation_step')
        await sysdata.save(update_fields=update_fields)
        return sysdata
    return None

async def delete_currency(sysdata_id: int):
    sysdata = await get_currency_by_id(sysdata_id)
    if sysdata:
        await sysdata.delete()
        return True
    return False