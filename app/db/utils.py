from tortoise import Tortoise

async def get_model_by_name(model_name: str):
    registered_models = Tortoise.apps['models']

    for registered_name, model in registered_models.items():
        if registered_name.lower() == model_name.lower():
            return model
    raise KeyError(f"Model '{model_name}' not found")