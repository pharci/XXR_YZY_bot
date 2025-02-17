from django.contrib import admin
from .models import User
from .models import UserActivity
from django.utils.html import format_html
from admin_app.orders.admin import PromocodeInline
from column_toggle.admin import ColumnToggleModelAdmin

@admin.register(UserActivity)
class UserActivityAdmin(ColumnToggleModelAdmin):
    list_display = ("user", "formatted_text", "device", "ip_address", "created_at")
    default_selected_columns = ['user', 'formatted_text', 'created_at']
    search_fields = ("user__username", "activity_type", "ip_address")
    list_filter = ("created_at", )

    def formatted_text(self, obj):
        return format_html(obj.activity_type.replace("\n", "<br>"))
    formatted_text.admin_order_field = 'activity_type'
    formatted_text.short_description = "Действие"

@admin.register(User)
class UserAdmin(ColumnToggleModelAdmin):
    list_display = ("avatar_thumbnail", "telegram", "telegram_id", 'contact', 'description', 'is_staff')
    default_selected_columns = ['avatar_thumbnail', 'telegram', 'contact']
    search_fields = ('username', 'contact')
    list_filter = ('is_staff', 'is_active')
    inlines = [PromocodeInline]

    def avatar_thumbnail(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.avatar.url)
        return "-"
    avatar_thumbnail.short_description = "Аватар"

    def telegram(self, obj):
        return format_html('<a href="https://t.me/{}">@{}</a>', obj.username, obj.username)
    telegram.short_description = "Telegram"