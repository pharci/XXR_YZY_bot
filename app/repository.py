from asgiref.sync import sync_to_async
from django.db import models

class DjangoRepo:
    @staticmethod
    @sync_to_async
    def create(model: models.Model, data: dict):
        return model.objects.create(**data)

    @staticmethod
    @sync_to_async
    def read(model: models.Model, obj_id: int):
        return model.objects.filter(id=obj_id).first()

    @staticmethod
    @sync_to_async
    def update(model: models.Model, obj_id: int, data: dict):
        obj = model.objects.filter(id=obj_id).first()
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
            obj.save()
            return obj
        return None

    @staticmethod
    @sync_to_async
    def delete(model: models.Model, obj_id: int):
        obj = model.objects.filter(id=obj_id).first()
        if obj:
            obj.delete()
            return True
        return False
    
    @staticmethod
    @sync_to_async
    def filter(model: models.Model, **kwargs):
        return list(model.objects.filter(**kwargs))
    
    @staticmethod
    @sync_to_async
    def call_model_method(obj, method_name, *args, **kwargs):
        method = getattr(obj, method_name, None)
        if method and callable(method):
            return method(*args, **kwargs)
        raise AttributeError(f"Method {method_name} not found on {obj.__class__.__name__}")