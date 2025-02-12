from django.contrib import admin
from .models import Order, OrderType, OrderStatus, Promocode, PromocodeUsage, Conversion, Graduation
from decimal import Decimal
import nested_admin
from django.utils.html import format_html

class PromocodeUsageInline(nested_admin.NestedTabularInline):
    model = PromocodeUsage
    extra = 0
    
@admin.register(PromocodeUsage)
class PromocodeUsageAdmin(admin.ModelAdmin):
    list_display = ('promocode', 'user', 'created_at')
    search_fields = ('promocode__code', 'user__username')
    list_filter = ('created_at',)


class PromocodeInline(nested_admin.NestedTabularInline):
    model = Promocode
    extra = 1

@admin.register(Promocode)
class PromocodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'user', 'order_type', 'conversion', 'discount', 'activations', 'max_activations', 'start_at', 'end_at', 'created_at')
    search_fields = ('code', 'user__username', 'order_type__name')
    list_filter = ('start_at', 'end_at')



    

@admin.register(OrderType)
class OrderTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    list_filter = ('name',)

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    list_filter = ('name',)




class OrderInline(nested_admin.NestedTabularInline):
    model = Order
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'contact', 'status', 'type', 'amount', 'amount_output', 'exchange_rate', 'created_at')
    search_fields = ('order_id', 'user__username', 'user__id')
    list_filter = ('status', 'type', 'created_at')

    readonly_fields = ('receive',)

    inlines = [PromocodeUsageInline]


    def receive(self, obj):
        if obj.amount and obj.exchange_rate:
            return format_html(f'<span>{round(((round(obj.amount / obj.currency.clean_course, 2) - obj.amount_output) * obj.currency.clean_course), 2)} {obj.currency.user_currency}</span>')
    receive.short_description = "Чистая прибыль"

    


@admin.register(Graduation)
class GraduationAdmin(admin.ModelAdmin):
    list_display = ('amount', 'adjustment', 'conversion_link')
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
class ConversionAdmin(admin.ModelAdmin):
    list_display = ('user_currency', 'exchange_currency', 'course', 'clean_course', 'created_at', 'updated_at')
    search_fields = ('user_currency', 'exchange_currency')
    list_filter = ('user_currency', 'exchange_currency')