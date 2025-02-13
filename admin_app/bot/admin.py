from django.contrib import admin
from .models import Bot, Study
from column_toggle.admin import ColumnToggleModelAdmin

@admin.register(Bot)
class BotAdmin(ColumnToggleModelAdmin):
    list_display = ("message_id", "name", "text", "created_at")
    default_selected_columns = ['message_id', 'name']

@admin.register(Study)
class StudyAdmin(ColumnToggleModelAdmin):
    list_display = ("name", "amount", "is_active", "created_at")
    default_selected_columns = ['name', 'amount', 'is_active']