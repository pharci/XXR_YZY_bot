from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
from app.core.config import settings
import time

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/webhook") or request.url.path.startswith("/login"):
            return await call_next(request)

        token = request.cookies.get("access_token")

        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

                if "exp" in payload and payload["exp"] < time.time():
                    return RedirectResponse(url="/login")

                request.state.user = payload
            except jwt.PyJWTError:
                return RedirectResponse(url="/login")
        else:
            if not request.url.path.startswith("/login"):
                return RedirectResponse(url="/login")
            
        response = await call_next(request)
        return response