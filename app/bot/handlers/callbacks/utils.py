from datetime import timedelta
from django.utils import timezone
from app.bot.keyboards import *
from app.bot.keyboards.keyboards import autokey
from admin_app.orders.models import Conversion, Order, Promocode, OrderTypeEnum
from admin_app.accounts.models import User, UserActivity
from admin_app.bot.models import Tariff
import time
import random
from app.repository import DjangoRepo


async def createOrder(call, data):
    user = (await DjangoRepo.filter(User, telegram_id=call.message.chat.id))[0]
    order_id = int(f"{int(time.time())}{random.randint(10, 99)}")
    amount_input = data.get('amount_input')
    amount_output = data.get('amount_output', None)
    course = data.get('course', None)
    clean_course = data.get('clean_course', None)
    conversion_id = data.get('conversion_id', None)
    code = data.get('code', None)
    promocode = (await DjangoRepo.filter(Promocode, code=code))[0] if code else None
    type = data.get('type')
    tariff_id = data.get('tariff_id', None)

    order = await DjangoRepo.create(Order, {
        'user': user,
        'contact': user.contact,
        'order_id': order_id,
        'type': type,
        'tariff': (await DjangoRepo.filter(Tariff, id=tariff_id))[0] if tariff_id else None,
        'currency': (await DjangoRepo.filter(Conversion, id=conversion_id))[0] if conversion_id else None,
        'amount': amount_input,
        'amount_output': amount_output,
        'exchange_course': course,
        'clean_course': clean_course,
        'promocode': promocode,
    })

    await DjangoRepo.create(UserActivity, {
        'user': user,
        'activity_type': 
            f"Создан заказ {order.order_id}:\n" \
            f"Тип: {order.get_type_display()}\n" \
            f"Промокод: {order.promocode.code}" if promocode else "Нет"
    })

    if promocode:
        await DjangoRepo.call_model_method(promocode, "increase_activation")
        


    text = await DjangoRepo.call_model_method(order, "get_text")

    await call.message.edit_text(text)
    await call.message.answer("Спасибо за заказ!", reply_markup=autokey({'Профиль': 'Profile', 'Меню': 'start'}))


async def checkPromocode(message, user, order_type, tariff_id = None, conversion_id = None):
    try:
        promocode = await DjangoRepo.filter(Promocode, code=message.text)

        if not promocode:
            await message.answer(f"Промокод с кодом {message.text} не найден.", reply_markup=autokey({'Вернуться': 'OrderPreview'}))
            return False
        else:
            promocode = (await DjangoRepo.filter(Promocode, code=message.text))[0]
        
        promocode_user = await DjangoRepo.call_model_method(promocode, "get_user")
        if promocode_user and promocode_user != user:
            await message.answer(f"Этот промокод принадлежит другому пользователю.", reply_markup=autokey({'Вернуться': 'OrderPreview'}))
            return False
        
        # Проверка на срок действия
        now = timezone.now()
        if promocode.start_at > now:
            await message.answer(f"Промокод еще не доступен, его можно использовать с {promocode.start_at.strftime('%d.%m.%Y %H:%M')}.", reply_markup=autokey({'Вернуться': 'OrderPreview'}))
            return False

        if promocode.end_at < now:
            await message.answer(f"Промокод просрочен, его срок действия завершился {promocode.end_at.strftime('%d.%m.%Y %H:%M')}.", reply_markup=autokey({'Вернуться': 'OrderPreview'}))
            return False

        # Проверка на количество активаций
        if promocode.activations >= promocode.max_activations:
            await message.answer(f"Промокод был использован максимально количество раз ({promocode.max_activations} раз).", reply_markup=autokey({'Вернуться': 'OrderPreview'}))
            return False
        
        # Проверка на тип заказа
        if promocode.order_type != order_type:
            await message.answer(f"Этот промокод предназначен для типа заказа: {promocode.order_type}.", reply_markup=autokey({'Вернуться': 'OrderPreview'}))
            return False

        # Проверка на валютную пару
        conversion = (await DjangoRepo.filter(Conversion, id=conversion_id))
        if conversion:
            conversion = conversion[0]
        promocode_conversion = await DjangoRepo.call_model_method(promocode, "get_conversion")
        if promocode_conversion and promocode_conversion != conversion:
            await message.answer(f"Этот промокод предназначен для валютной пары: {promocode_conversion}.", reply_markup=autokey({'Вернуться': 'OrderPreview'}))
            return False

        # Проверка на тариф
        tariff = (await DjangoRepo.filter(Tariff, id=tariff_id))
        if tariff:
            tariff = tariff[0]
        promocode_tariff = await DjangoRepo.call_model_method(promocode, "get_tariff")
        if promocode_tariff and promocode_tariff != tariff:
            await message.answer(f"Этот промокод предназначен для тарифа: {promocode_tariff.name}", reply_markup=autokey({'Вернуться': 'OrderPreview'}))
            return False

        # Если все проверки прошли успешно
        await message.answer(f"Промокод {promocode.code} успешно применен!", reply_markup=autokey({'Продолжить': 'OrderPreview', 'Отмена': 'start'}))
        return True

    except Exception as e:
        await message.answer(f"Произошла ошибка при проверке промокода.", reply_markup=autokey({'Вернуться': 'OrderPreview'}))
        return False