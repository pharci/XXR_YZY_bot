from django.contrib import admin
from .models import Order, OrderType, OrderStatus, Promocode, PromocodeUsage, Conversion, Graduation
from decimal import Decimal
import nested_admin
from django.utils.html import format_html
from column_toggle.admin import ColumnToggleModelAdmin
from import_export.admin import ExportMixin
from import_export.resources import ModelResource


class PromocodeUsageInline(nested_admin.NestedTabularInline):
    model = PromocodeUsage
    extra = 0
    
@admin.register(PromocodeUsage)
class PromocodeUsageAdmin(ColumnToggleModelAdmin):
    list_display = ('promocode', 'user', 'created_at')
    default_selected_columns = ['promocode', 'user', 'created_at']
    search_fields = ('promocode__code', 'user__username')
    list_filter = ('created_at',)


class PromocodeInline(nested_admin.NestedTabularInline):
    model = Promocode
    extra = 1

@admin.register(Promocode)
class PromocodeAdmin(ColumnToggleModelAdmin):
    list_display = ('code', 'user', 'order_type', 'conversion', 'discount', 'activations', 'max_activations', 'start_at', 'end_at', 'created_at')
    default_selected_columns = ['code', 'user', 'order_type', 'conversion', 'discount', 'activations', 'created_at']
    search_fields = ('code', 'user__username', 'order_type__name')
    list_filter = ('start_at', 'end_at')



    

@admin.register(OrderType)
class OrderTypeAdmin(ColumnToggleModelAdmin):
    list_display = ('name', 'description')
    default_selected_columns = ['name', 'description']
    search_fields = ('name',)
    list_filter = ('name',)

@admin.register(OrderStatus)
class OrderStatusAdmin(ColumnToggleModelAdmin):
    list_display = ('name', 'description')
    default_selected_columns = ['name', 'description']
    search_fields = ('name',)
    list_filter = ('name',)





class OrderResource(ModelResource):
    class Meta:
        model = Order

class OrderInline(nested_admin.NestedTabularInline):
    model = Order
    extra = 1

@admin.register(Order)
class OrderAdmin(ExportMixin, ColumnToggleModelAdmin):
    resource_class = OrderResource
    list_display = ('order_id', 'telegram', 'contact', 'status', 'type', "currency", 'input_amount', 'output_amount', "receive", 'exchange_rate', 'created_at')
    default_selected_columns = ['order_id', 'telegram', 'contact', 'status', 'type', 'input_amount', 'output_amount', 'exchange_rate', 'created_at']
    search_fields = ('order_id', 'user__username', "contact")
    list_filter = ('status', 'type', 'created_at')

    readonly_fields = ('receive',)

    inlines = [PromocodeUsageInline]

    def input_amount(self, obj):
        if obj.amount and obj.currency:
            return format_html(f'<span style="color: blue;">{obj.amount} {obj.currency.user_currency}</span>')
    input_amount.short_description = "Сумма"

    def output_amount(self, obj):
        if obj.amount and obj.currency:
            return format_html(f'<span style="color: blue;">{obj.amount_output} {obj.currency.exchange_currency}</span>')
    output_amount.short_description = "К получению"

    def receive(self, obj):
        if obj.amount and obj.exchange_rate:
            return format_html(f'<span style="color: green;">{round(((round(obj.amount / obj.currency.clean_course, 2) - obj.amount_output) * obj.currency.clean_course), 2)} {obj.currency.user_currency}</span>')
    receive.short_description = "Чистая прибыль"

    def telegram(self, obj):
        return format_html('<a style="color: red;" href="https://t.me/{}">@{}</a>', obj.user.username, obj.user.username)
    telegram.short_description = "Пользователь"

    


@admin.register(Graduation)
class GraduationAdmin(ColumnToggleModelAdmin):
    list_display = ('amount', 'adjustment', 'conversion_link')
    default_selected_columns = ['amount', 'adjustment', 'conversion_link']
    search_fields = ('amount', 'adjustment')
    list_filter = ('amount', 'adjustment')

    def conversion_link(self, obj):
        conversions = obj.conversions.all()
        if conversions.exists():
            return format_html(
                ", ".join(
                    f'<a href="/admin/orders/conversion/{c.id}/">{c}</a>'
                    for c in conversions
                )
            )
        return "Нет конверсий"

    conversion_link.short_description = "Конвертация"

@admin.register(Conversion)
class ConversionAdmin(ColumnToggleModelAdmin):
    list_display = ('user_currency', 'exchange_currency', 'course', 'clean_course', 'created_at', 'updated_at')
    default_selected_columns = ['user_currency', 'exchange_currency', 'course', 'clean_course', 'updated_at']
    search_fields = ('user_currency', 'exchange_currency')
    list_filter = ('user_currency', 'exchange_currency', 'updated_at')