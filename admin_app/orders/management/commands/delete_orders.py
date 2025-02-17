from django.core.management.base import BaseCommand
from admin_app.orders.models import Order

class Command(BaseCommand):
    help = "Удаляет все заказы"

    def handle(self, *args, **kwargs):
        total_orders = Order.objects.count()

        if total_orders == 0:
            self.stdout.write(self.style.WARNING("Нет заказов для удаления."))
            return

        self.stdout.write(self.style.NOTICE(f"Начинаем удаление {total_orders} заказов..."))

        batch_size = 10_000  # Удаляем по 10 000 за раз
        while Order.objects.exists():
            orders_to_delete = Order.objects.all()[:batch_size].iterator()
            ids_to_delete = [order.id for order in orders_to_delete]
            Order.objects.filter(id__in=ids_to_delete).delete()
            self.stdout.write(self.style.SUCCESS(f"Удалено {len(ids_to_delete)} заказов..."))

        self.stdout.write(self.style.SUCCESS(f"Все {total_orders} заказов успешно удалены!"))

