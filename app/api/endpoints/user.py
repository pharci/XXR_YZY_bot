from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse
from app.db.models import *
from app.db.admin import admin_models
from .auth import get_current_user
from datetime import datetime
from typing import Optional

templates = Jinja2Templates(directory="app/admin_panel/templates")

router = APIRouter()

def get_model_by_name(name: str):
    models = {
        "users": User,
        "orders": Order,
        "sysdata": Sysdata,
        "promocode": Promoсode,
    }
    return models.get(name)

def datetime_format(value, format="%d.%m.%Y %H:%M:%S"):
    if isinstance(value, datetime):
        return value.strftime(format)
    return value
templates.env.filters["strftime"] = datetime_format


@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("main.html", {"request": request})


@router.get("/admin/{model_name}", response_class=HTMLResponse)
async def list_records(
    model_name: str, 
    request: Request, 
    user: dict = Depends(get_current_user),
    text_filter: Optional[str] = None, 
    select_filter: Optional[str] = None
):
    admin_model = admin_models.get(model_name)
    if not admin_model:
        raise HTTPException(status_code=404, detail="Модель не найдена")

    model = get_model_by_name(model_name)
    if not model:
        raise HTTPException(status_code=404, detail="Модель не найдена")

    query = model.all()

    if text_filter:
        query = query.filter(**{admin_model.filter: text_filter})
    
    if select_filter:
        query = query.filter(**{admin_model.filter_btn: select_filter})

    records = await query.values()

    displayed_records = [{
        field: (record[field].value if isinstance(record[field], OrderStatus) else record[field])
        for field in admin_model.display_fields
    }
        for record in records
    ]

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JSONResponse({"records": displayed_records})
    
    return templates.TemplateResponse("admin_list.html", {
        "request": request,
        "records": displayed_records,
        "model_name": model_name,
        "admin_model": admin_model,
        "user": user,
    })

@router.get("/admin/{model_name}/{record_id}", response_class=HTMLResponse)
async def record_detail(model_name: str, record_id: int, request: Request, user: dict = Depends(get_current_user)):

    admin_model = admin_models.get(model_name)
    if not admin_model:
        raise HTTPException(status_code=404, detail="Модель не найдена")

    model = get_model_by_name(model_name)
    if not model:
        raise HTTPException(status_code=404, detail="Модель не найдена")

    record = await model.filter(id=record_id).select_related(*admin_model.related_fields).first()

    detailed_record = {field: getattr(record, field) for field in admin_model.detail_fields}

    return templates.TemplateResponse("admin_detail.html", {
        "request": request, 
        "record": detailed_record,
        "model_name": model_name,
        "admin_model": admin_model,
        "user": user,
    })

@router.put("/admin/{model_name}/update/{record_id}")
async def update_record(model_name: str, record_id: int, request: Request):
    model = get_model_by_name(model_name)
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
    model = get_model_by_name(model_name)
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
        raise HTTPException(status_code=404, detail="Доступ запрещен")
    
    fields = [field for field in admin_model.fields if field.editable]

    return templates.TemplateResponse("create_record.html", {
        "request": request,
        "admin_model": admin_model,
        "fields": fields,
    })


@router.post("/admin/{model_name}/create/")
async def create_record(model_name: str, request: Request):
    admin_model = admin_models.get(model_name)
    if not admin_model:
        raise HTTPException(status_code=404, detail="Модель не найдена")

    data = await request.json()

    model = get_model_by_name(model_name)
    record = model(**data)

    await record.save()

    print(record)

    return JSONResponse({"status": "success", "message": "Запись успешно создана"})