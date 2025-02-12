from django.contrib import admin
from .models import User
from .models import UserActivity
from django.utils.html import format_html
import nested_admin
from admin_app.orders.admin import OrderInline, PromocodeInline, PromocodeUsageInline

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ("user", "activity_type", "device", "ip_address", "created_at")
    search_fields = ("user__username", "activity_type", "ip_address")
    list_filter = ("activity_type", "created_at")

class UserActivityInline(nested_admin.NestedTabularInline):
    model = UserActivity
    extra = 1

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("avatar_thumbnail", "telegram", "telegram_id", 'contact', 'description', 'is_staff')
    search_fields = ('username', 'contact')
    list_filter = ('is_staff', 'is_active')
    inlines = [OrderInline, PromocodeInline, UserActivityInline, PromocodeUsageInline]

    def avatar_thumbnail(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.avatar.url)
        return "-"
    avatar_thumbnail.short_description = "Аватар"

    def telegram(self, obj):
        return format_html('<a href="https://t.me/{}">@{}</a>', obj.username, obj.username)
    telegram.short_description = "Telegram"