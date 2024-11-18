from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse
from app.db.models import *
from app.db.admin import admin_registry
from .auth import get_current_user
from datetime import datetime, timedelta
from typing import Optional
from app.db.utils import get_model_by_name
from pytz import timezone
from tortoise.queryset import Q
from fastapi.encoders import jsonable_encoder

templates = Jinja2Templates(directory="app/admin_panel/templates")

router = APIRouter()

def serialize_data(value):
    if isinstance(value, datetime):
        moscow_tz = timezone("Europe/Moscow")
        value = value.astimezone(moscow_tz)
        return value.strftime("%d.%m.%Y %H:%M")
    return value 

@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


@router.get("/admin/{model_name}", response_class=HTMLResponse)
async def list_records(
    model_name: str,
    request: Request,
    q: Optional[str] = None, 
    select: Optional[str] = None,
    date: Optional[str] = None,
    ):
    
    model = await get_model_by_name(model_name)
    admin = admin_registry.get_admin_class(model)

    list_display_names = [field.name for field in admin.list_display]
    query = model.all()

    if q:
        for filter in admin.search_fields:
            query = query.filter(**{filter.name: q})
    
    if select:
        query = query.filter(**{admin.list_filter: select})

    if date:
        date = datetime.strptime(date, "%Y-%m-%d")
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(
            Q(**{f"created_at__gte": date}) & Q(**{f"created_at__lt": date + timedelta(days=1)})
        )

    records = await query.values("id", *list_display_names)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JSONResponse({"records":  jsonable_encoder(records)})
    
    return templates.TemplateResponse("admin_list.html", {
        "request": request,
        "records": records,
        "admin": admin,
    })

@router.get("/admin/{model_name}/{record_id}", response_class=HTMLResponse)
async def record_detail(model_name: str, record_id: int, request: Request):

    admin_model = admin_models.get(model_name)
    if not admin_model:
        raise HTTPException(status_code=404, detail="Модель не найдена")

    model = await get_model_by_name(model_name)
    if not model:
        raise HTTPException(status_code=404, detail="Модель не найдена")
    
    record = await model.filter(id=record_id).select_related(*admin_model.related_fields).first()
    detailed_record = {
        field: serialize_data(getattr(record, field))
        for field in admin_model.detail_fields
    }

    return templates.TemplateResponse("admin_detail.html", {
        "request": request, 
        "record": detailed_record,
        "model_name": model_name,
        "admin_model": admin_model,
    })

@router.put("/admin/{model_name}/update/{record_id}")
async def update_record(model_name: str, record_id: int, request: Request):
    model = await get_model_by_name(model_name)
    if not model:
        raise HTTPException(status_code=404, detail="Модель не найдена")

    data = await request.json()

    try:
        record = await model.get(id=record_id)
    except model.DoesNotExist:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    for field, value in data.items():
        if hasattr(record, field):
            setattr(record, field, value)

    await record.save()
    return JSONResponse({"status": "success", "message": "Запись успешно обновлена"})


@router.delete("/admin/{model_name}/delete/{record_id}")
async def delete_record(model_name: str, record_id: int):
    model = await get_model_by_name(model_name)
    if not model:
        raise HTTPException(status_code=404, detail="Модель не найдена")

    record = await model.get(id=record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    await record.delete()

    return {"status": "success", "message": "Запись успешно удалена"}


@router.get("/admin/{model_name}/create/")
async def create_record_page(model_name: str, request: Request):
    admin_model = admin_models.get(model_name)
    if not admin_model:
        raise HTTPException(status_code=404, detail="Модель не найдена")
    if not admin_model.create_records:
        raise HTTPException(status_code=403, detail="Создание записей запрещено")

    fields = [field for field in admin_model.fields if field.editable]
    
    related_data = {}
    for field in fields:
        if field.related_model:
            related_model_name = field.related_model
            related_model = admin_models.get(related_model_name)
            if related_model:
                model = await get_model_by_name(related_model_name)
                related_data[related_model_name] = await model.all()
                
    return templates.TemplateResponse("create_record.html", {
        "request": request,
        "admin_model": admin_model,
        "related_data": related_data,  # Данные для выпадающих списков
    })


@router.post("/admin/{model_name}/create/")
async def create_record(model_name: str, request: Request):
    admin_model = admin_models.get(model_name)
    if not admin_model:
        raise HTTPException(status_code=404, detail="Модель не найдена")

    data = await request.json()

    model = await get_model_by_name(model_name)
    record = model(**data)

    await record.save()

    print(record)

    return JSONResponse({"status": "success", "message": "Запись успешно создана"})