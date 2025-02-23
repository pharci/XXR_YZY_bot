from django.contrib import admin
from .models import User
from .models import PromocodeUsage
from django.utils.html import format_html
from admin_app.orders.admin import PromocodeInline
from column_toggle.admin import ColumnToggleModelAdmin
import nested_admin

@admin.register(PromocodeUsage)
class UserActivityAdmin(ColumnToggleModelAdmin):
    list_display = ("user", "order", "promocode", "created_at")
    default_selected_columns = ["user", "order", "promocode", "created_at"]
    readonly_fields = ("user", "order", "promocode", "created_at") 
    search_fields = ("user", "order", "promocode")

@admin.register(User)
class UserAdmin(nested_admin.NestedModelAdmin, ColumnToggleModelAdmin):
    list_display = ("telegram_id", "telegram", 'contact', 'description', 'is_staff')
    default_selected_columns = ["telegram_id", 'telegram', 'contact', "get_profit_by_month"]
    search_fields = ('username', 'contact')
    list_filter = ('is_staff', )
    readonly_fields = ("get_profit_by_month", ) 
    inlines = [PromocodeInline]

    def telegram(self, obj):
        return format_html('<a href="https://t.me/{}">@{}</a>', obj.username, obj.username)
    telegram.short_description = "Telegram"

    def get_profit_by_month(self, obj):
        months = obj.get_profit_by_month()
        months_html = "<table style='width: 100%; border: 1px solid #ddd; border-collapse: collapse;'>"
        months_html += "<tr><th style='padding: 8px; text-align: left; background-color: #f2f2f2;'>Месяц</th><th style='padding: 8px; text-align: left; background-color: #f2f2f2;'>Прибыль (₽)</th></tr>"

        for month in months:
            months_html += format_html(
                "<tr><td style='padding: 8px; border: 1px solid #ddd;'>{}</td><td style='padding: 8px; border: 1px solid #ddd;'>{}</td></tr>",
                month['month'],
                month['profit']
            )

        months_html += "</table>"
        
        return format_html(months_html)
    get_profit_by_month.short_description = 'Прибыль по месяцам'