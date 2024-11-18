from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from app.core.config import settings
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
import hashlib
import hmac
import time
import jwt
from datetime import datetime, timedelta
from app.core.config import settings
from app.crud.user import get_or_create_user, get_user
from app.schemas.user import UserCreate

templates = Jinja2Templates(directory="app/admin_panel/templates")

router = APIRouter()

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_telegram_data(telegram_data, token):
    auth_date = telegram_data.get('auth_date')
    hash_value = telegram_data.get('hash')
    
    if not auth_date or not hash_value:
        return False

    data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(telegram_data.items()) if k != 'hash')

    secret_key = hashlib.sha256(token.encode()).digest()
    check_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    return hmac.compare_digest(check_hash, hash_value) and (int(time.time()) - int(auth_date)) < 86400

async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=403, detail="Authentication credentials were not provided")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        user = await get_user(user_id)
        
        if not user_id:
            raise HTTPException(status_code=403, detail="Invalid token: User ID not found")
        return {"user_id": user_id }
    
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

@router.get("/login")
async def login_via_telegram(request: Request):
    telegram_data = request.query_params
    if "hash" in telegram_data:
        if not verify_telegram_data(telegram_data, token=settings.TELEGRAM_TOKEN):
            raise HTTPException(status_code=403, detail="Telegram verification failed.")
        
        if telegram_data.get("username"):
            username = telegram_data.get("username")
        else:
            username = "Отсутствует"
        
        user_data = UserCreate(user_id=telegram_data.get("id"), username=username, first_name=telegram_data.get("first_name"))
        user = await get_or_create_user(user_data)

        if not(user.is_staff or user.is_superuser):
            raise HTTPException(status_code=403, detail="No access.")

        token = create_access_token(data={"user_id": user.user_id, "first_name": user.first_name})

        response = RedirectResponse("/admin")
        response.set_cookie(key="access_token", value=token, httponly=True)
        return response
    
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse("/login")
    response.delete_cookie("access_token")
    return response