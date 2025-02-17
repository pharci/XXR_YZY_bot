from django.contrib import admin
from .models import Bot, Tariff, Category
from column_toggle.admin import ColumnToggleModelAdmin

@admin.register(Bot)
class BotAdmin(ColumnToggleModelAdmin):
    list_display = ("message_id", "name", "text", "created_at")
    default_selected_columns = ['message_id', 'name']

@admin.register(Tariff)
class TariffAdmin(ColumnToggleModelAdmin):
    list_display = ("name", "category", "amount", "is_active", "created_at")
    default_selected_columns = [ 'name', "catrgory", 'amount', 'is_active']

@admin.register(Category)
class CategoryAdmin(ColumnToggleModelAdmin):
    list_display = ("name", "text", "is_active", "created_at")
    default_selected_columns = ['name', 'text', 'is_active', "created_at"]