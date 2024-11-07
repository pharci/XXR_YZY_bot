from tortoise import Tortoise

from app.db.models.user import User, UserActivity
from app.db.models.order import Order
from app.db.models.sysdata import Sysdata, PromoCode

def init_models():
    Tortoise.init_models(["app.db.models.user"], "models") 