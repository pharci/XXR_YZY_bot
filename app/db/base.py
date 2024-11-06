from tortoise import Tortoise

from app.db.models.user import User
from app.db.models.models import UserActivity, Order, Sysdata, PromoCode

def init_models():
    Tortoise.init_models(["app.db.models.user"], "models") 