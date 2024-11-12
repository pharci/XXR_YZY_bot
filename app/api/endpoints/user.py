from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse
from app.db.models import *
from app.db.admin import admin_models

templates = Jinja2Templates(directory="app/admin_panel/templates")

router = APIRouter()

@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

def get_model_by_name(name: str):
    models = {
        "users": User,
        "orders": Order,
        "sysdata": Sysdata,
        "promocode": Promoсode,
    }
    return models.get(name)

@router.get("/admin/{model_name}/", response_class=HTMLResponse)
async def list_records(model_name: str, request: Request):
    admin_model = admin_models.get(model_name)
    if not admin_model:
        raise HTTPException(status_code=404, detail="Модель не найдена")

    model = get_model_by_name(model_name)
    if not model:
        raise HTTPException(status_code=404, detail="Модель не найдена")

    records = await model.all().values()
    displayed_records = [
        {field: record[field] for field in admin_model.display_fields} for record in records
    ]

    return templates.TemplateResponse("admin_list.html", {
        "request": request, 
        "records": displayed_records,
        "model_name": model_name,
        "admin_model": admin_model
    })

@router.get("/admin/{model_name}/{record_id}/", response_class=HTMLResponse)
async def record_detail(model_name: str, record_id: int, request: Request):

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
        "admin_model": admin_model
    })

@router.put("/admin/{model_name}/update/{record_id}/")
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

@router.delete("/admin/{model_name}/delete/{record_id}/")
async def delete_record(model_name: str, record_id: int):
    model = get_model_by_name(model_name)
    if not model:
        raise HTTPException(status_code=404, detail="Модель не найдена")

    record = await model.get(id=record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    await record.delete()

    return {"status": "success", "message": "Запись успешно удалена"}