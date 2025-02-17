from django.core.management.base import BaseCommand
from faker import Faker
import random
from django.utils.timezone import now
from admin_app.orders.models import Order, Conversion, Tariff, Promocode
from admin_app.accounts.models import User

fake = Faker()

def generate_unique_order_id():
    while True:
        order_id = random.randint(1, 9_999_999_999_999)
        if not Order.objects.filter(order_id=order_id).exists():
            return order_id

class Command(BaseCommand):
    help = "Генерирует 1 000 000 тестовых заказов"

    def handle(self, *args, **kwargs):
        users = list(User.objects.all())
        currencies = list(Conversion.objects.all())
        tariffs = list(Tariff.objects.all())
        promocodes = list(Promocode.objects.all())

        orders = []

        for _ in range(100000):
            user = random.choice(users) if users else None
            currency = random.choice(currencies) if currencies else None
            tariff = random.choice(tariffs) if tariffs else None
            promocode = random.choice(promocodes) if promocodes else None

            amount = round(random.uniform(100, 10000), 2)
            exchange_course = round(random.uniform(10, 20), 2)
            clean_course = round(random.uniform(9, 19), 2)
            amount_output = round(amount / exchange_course, 2)
            profit = round((amount / clean_course - amount_output) * clean_course, 2)

            orders.append(Order(
                user=user,
                order_id=generate_unique_order_id(),
                type=random.choice(["study", "exchange", "safepay"]),
                status=random.choice([choice[0] for choice in Order.OrderStatusChoices.choices]),
                contact=fake.phone_number(),
                tariff=tariff,
                currency=currency,
                amount=amount,
                amount_output=amount_output,
                exchange_course=exchange_course,
                clean_course=clean_course,
                profit=profit,
                promocode=promocode,
                created_at=now(),
                updated_at=now()
            ))

        Order.objects.bulk_create(orders, batch_size=100_000)
        self.stdout.write(self.style.SUCCESS("100000 заказов успешно созданы!"))