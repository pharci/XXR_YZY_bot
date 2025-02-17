from django.contrib import admin
from .models import Order, Promocode, Conversion
from decimal import Decimal
import nested_admin
from django.utils.html import format_html
from column_toggle.admin import ColumnToggleModelAdmin
from import_export.admin import ExportActionMixin, ImportExportModelAdmin
from import_export.resources import ModelResource
from import_export import fields
from import_export.widgets import ForeignKeyWidget
from admin_app.accounts.models import User
from admin_app.orders.models import Conversion, Promocode
from admin_app.bot.models import Tariff
from rangefilter.filters import DateRangeFilter

class PromocodeInline(nested_admin.NestedTabularInline):
    model = Promocode
    extra = 1

@admin.register(Promocode)
class PromocodeAdmin(ColumnToggleModelAdmin):
    list_display = ('code', 'user', 'order_type', 'conversion', 'discount', 'activations', 'max_activations', 'start_at', 'end_at', 'created_at')
    default_selected_columns = ['code', 'user', 'order_type', 'conversion', 'discount', 'activations', 'created_at']
    search_fields = ('code', 'user__username', 'order_type__name')
    list_filter = ('start_at', 'end_at')



@admin.register(Conversion)
class ConversionAdmin(ColumnToggleModelAdmin):
    list_display = ('user_currency', 'exchange_currency', 'course', 'clean_course', 'created_at', 'updated_at')
    default_selected_columns = ['user_currency', 'exchange_currency', 'course', 'clean_course', 'updated_at']
    search_fields = ('user_currency', 'exchange_currency')
    list_filter = ('user_currency', 'exchange_currency', 'updated_at')


class CustomConversionWidget(ForeignKeyWidget):
    def render(self, value, obj=None, **kwargs):
        if value:
            return f"{value.user_currency} -> {value.exchange_currency}"
        return ""
class OrderResource(ModelResource):
    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=ForeignKeyWidget(User, field='username')
    )

    currency = fields.Field(
        column_name='currency',
        attribute='currency',
        widget=CustomConversionWidget(Conversion, field='user_currency')
    )

    tariff = fields.Field(
        column_name='tariff',
        attribute='tariff',
        widget=ForeignKeyWidget(Tariff, field='name')
    )

    promocode = fields.Field(
        column_name='promocode',
        attribute='promocode',
        widget=ForeignKeyWidget(Promocode, field='code')
    )

    class Meta:
        model = Order


@admin.register(Order)
class OrderAdmin(ColumnToggleModelAdmin, ImportExportModelAdmin, ExportActionMixin):
    list_per_page = 300
    resource_class = OrderResource
    list_display = ('order_id', 'telegram', 'contact', 'status', 'type', "tariff", "currency", 'input_amount', 'output_amount', "receive", 'exchange_course', 'clean_course', 'promocode', 'created_at')
    default_selected_columns = ['order_id', 'telegram', 'contact', 'status', 'type', "tariff", 'input_amount', 'output_amount', 'exchange_course', 'clean_course', 'promocode', 'created_at']
    search_fields = ('order_id', 'user__username', "contact")
    list_filter = ('status', 'type', ('created_at', DateRangeFilter),)
    exclude = ('amount', 'amount_output', 'profit')
    readonly_fields = ('order_id', 'type', "tariff", 'promocode', 'currency', 'exchange_course', 'clean_course', 'input_amount', 'output_amount', 'receive',) 

    def input_amount(self, obj):
        if obj.amount and obj.currency:
            return format_html(f'<span style="color: blue;">{obj.amount} {obj.currency.user_currency}</span>')
        elif obj.amount and not obj.currency:
            return format_html(f'<span style="color: blue;">{obj.amount}₽</span>')
    input_amount.admin_order_field = 'amount'
    input_amount.short_description = "Сумма"

    def output_amount(self, obj):
        if obj.amount and obj.currency:
            return format_html(f'<span style="color: blue;">{obj.amount_output} {obj.currency.exchange_currency}</span>')
    output_amount.admin_order_field = 'amount_output'
    output_amount.short_description = "К получению"

    def receive(self, obj=None):
        if obj.amount and obj.exchange_course:
            return format_html(f'<span style="color: green;">{obj.profit }₽</span>')
    receive.short_description = "Чистая прибыль"

    def telegram(self, obj):
        return format_html('<a style="color: red;" href="https://t.me/{}">@{}</a>', obj.user.username, obj.user.username)
    telegram.admin_order_field = 'user__username'
    telegram.short_description = "Пользователь"

    def get_list_display(self, request):
        list_display = super().get_list_display(request)

        # Проверяем разрешение для поля 'clean_course'
        if not request.user.has_perm('orders.can_view_clean_course'):
            list_display = [field for field in list_display if field != "clean_course"]

        # Проверяем разрешение для поля 'receive'
        if not request.user.has_perm('orders.can_view_receive'):
            list_display = [field for field in list_display if field != "receive"]

        return list_display

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)

        # Проверяем разрешение для поля 'clean_course'
        if not request.user.has_perm('orders.can_view_clean_course'):
            fields = [field for field in fields if field != "clean_course"]

        # Проверяем разрешение для поля 'receive'
        if not request.user.has_perm('orders.can_view_receive'):
            fields = [field for field in fields if field != "receive"]

        return fields