from django.contrib import admin
from .models import Order, Promocode, Conversion, TransactionReceiving, TransactionSending, PaymentCard, PromocodeUsage, AlipayAccounts
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
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import localtime
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.db.models import Sum, Avg, Q

@admin.register(PromocodeUsage)
class UserActivityAdmin(ColumnToggleModelAdmin):
    list_display = ("user", "order", "promocode", "created_at")
    default_selected_columns = ["user", "order", "promocode", "created_at"]
    readonly_fields = ("user", "order", "promocode", "created_at") 
    search_fields = ("user", "order", "promocode")


class UserAutocomplete(admin.ModelAdmin):
    search_fields = ['name', 'contact']

    def get_search_results(self, request, queryset, search_term):
        return queryset.filter(Q(name__icontains=search_term) | Q(contact__icontains=search_term))

class PromocodeInline(nested_admin.NestedStackedInline):
    model = Promocode
    extra = 1

@admin.register(Promocode)
class PromocodeAdmin(ColumnToggleModelAdmin):
    list_display = ('code', 'user', 'order_type', 'conversion', 'discount', "reuse", 'activations', 'max_activations', 'start_at', 'end_at', 'created_at')
    default_selected_columns = ['code', 'user', 'order_type', 'conversion', 'discount', 'activations', 'created_at']
    search_fields = ('code', 'user__username', 'order_type__name')
    list_filter = ('start_at', 'end_at')
    autocomplete_fields = ['user']

@admin.register(Conversion)
class ConversionAdmin(ColumnToggleModelAdmin):
    list_display = ('user_currency', 'exchange_currency', 'course', 'clean_course', 'created_at', 'updated_at')
    default_selected_columns = ['user_currency', 'exchange_currency', 'course', 'clean_course', 'updated_at']
    search_fields = ('user_currency', 'exchange_currency')
    list_filter = ('user_currency', 'exchange_currency', 'updated_at')

@admin.register(AlipayAccounts)
class AlipayAccountsAdmin(ColumnToggleModelAdmin):
    list_display = ('name', 'account_id', 'created_at')
    default_selected_columns = ['name', 'account_id', 'created_at']
    search_fields = ('name', 'account_id', )

@admin.register(PaymentCard)
class PaymentCardAdmin(ColumnToggleModelAdmin):
    list_display = ('name', 'card_number', 'created_at')
    default_selected_columns = ['name', 'card_number', 'created_at']
    search_fields = ('name', 'card_number', )


class TransactionReceivingInline(nested_admin.NestedTabularInline):
    model = TransactionReceiving
    extra = 0
    readonly_fields = ('amount_usdt', "transaction_date")

    def get_formset(self, request, obj=None, **kwargs):
            formset = super().get_formset(request, obj, **kwargs)
            if obj and obj.currency: 
                formset.form.base_fields['amount'].label = f"СУММА В {obj.currency.user_currency}"
            return formset

class TransactionSendingInline(nested_admin.NestedTabularInline):
    model = TransactionSending
    extra = 0
    fields = ("alipay_id_display", "alipay_account", "amount", "exchange_course", 'amount_usdt', "transaction_date")
    readonly_fields = ('alipay_id_display', 'amount_usdt', "transaction_date")

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        
        if obj and obj.currency: 
            formset.form.base_fields['amount'].label = f"СУММА В {obj.currency.exchange_currency}"
        return formset
    
    def alipay_id_display(self, obj):
        html_content = format_html(
            '''
            <a href="#" onclick="copyToClipboard('{}'); return false;" 
            style="background-color: #4CAF50; color: white; padding: 5px 10px; text-align: center; text-decoration: none; display: inline-block; font-size: 14px; cursor: pointer; border-radius: 8px; transition: background-color 0.3s;">
            {}
            </a> 
            <div id="copyMessage" style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background-color: #4CAF50; color: white; padding: 10px 20px; border-radius: 5px; display: none; font-size: 14px;">
                Номер скопирован в буфер обмена!
            </div>
            <script type="text/javascript">
                function copyToClipboard(text) {{
                    const textarea = document.createElement('textarea');
                    textarea.value = text;
                    document.body.appendChild(textarea);
                    textarea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textarea);
                    
                    // Показываем сообщение
                    var message = document.getElementById('copyMessage');
                    message.style.display = 'block';
                    
                    // Скрываем сообщение через 2 секунды
                    setTimeout(function() {{
                        message.style.display = 'none';
                    }}, 2000);
                }}
            </script>
            ''',
            obj.alipay_account.account_id,
            obj.alipay_account.account_id,
        )
        
        return mark_safe(html_content) 
    alipay_id_display.short_description = "Номер Alipay"

class CustomConversionWidget(ForeignKeyWidget):
    def render(self, value, obj=None, **kwargs):
        if value:
            return f"{value.user_currency} -> {value.exchange_currency}"
        return ""
    
class OrderResource(ModelResource):
    class Meta:
        model = Order
        exclude = ('id', )

    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=ForeignKeyWidget(User, field='username')
    )

    admin = fields.Field(
        column_name='admin',
        attribute='admin',
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

    sum_of_transactions = fields.Field(column_name='sum_of_transactions')
    def dehydrate_sum_of_transactions(self, order):
        total_amount = order.transactions_r.aggregate(Sum('amount'))['amount__sum']
        return total_amount if total_amount else "-"

    average_course = fields.Field(column_name='average_course')
    def dehydrate_average_course(self, order):
        average_course = order.transactions_r.aggregate(Avg('exchange_course'))['exchange_course__avg']
        return round(average_course, 2) if average_course else "-"

    sum_of_usdt = fields.Field(column_name='sum_of_usdt')
    def dehydrate_sum_of_usdt(self, order):
        total_usdt = order.transactions_r.aggregate(Sum('amount_usdt'))['amount_usdt__sum']
        return round(total_usdt, 2) if total_usdt else "-"



class AdminAutocomplete(admin.ModelAdmin):
    search_fields = ['name', 'contact']

    def get_search_results(self, request, queryset, search_term):
        return queryset.filter(Q(name__icontains=search_term) | Q(contact__icontains=search_term))
    

@admin.register(Order)
class OrderAdmin(nested_admin.NestedModelAdmin, ColumnToggleModelAdmin, ImportExportModelAdmin, ExportActionMixin):
    list_per_page = 150
    autocomplete_fields = ['admin']
    resource_class = OrderResource
    fieldsets = (
        ("Основная информация", {"fields": ("order_id_display", 
                                            "user",
                                            "admin",
                                            "contact", 
                                            "status", 
                                            "type", 
                                            "input_amount", 
                                            "promocode")}),
        ("Обмен", {"fields": ("currency",
                              "output_amount",
                              "exchange_course",
                              ), "classes": ("wide",)}),
        ("Обучение", {"fields": ("tariff",), "classes": ("collapse",)}),
        ("Бизнес информация", {"fields": ("clean_course", 
                                          "profit_display", 
                                          "admin_profit_display", 
                                          "sum_of_transactions",
                                          "average_course",
                                          "sum_of_usdt",
                                          "order_history"
                                          ), "classes": ("wide",)}),
    )

    list_display = ('order_id', 'telegram', 'admin_display', 'contact', 'status', 'type', "tariff", "currency", 'input_amount', 'output_amount', "profit_display", "admin_profit_display", 'exchange_course', 'clean_course', 'promocode', 'created_at')
    default_selected_columns = ['order_id', 'telegram', "admin_display", 'contact', 'status', 'type', "tariff", 'input_amount', 'output_amount', 'exchange_course', 'clean_course', 'promocode', 'created_at']
    search_fields = ('order_id', 'user__username', "contact", 'admin__username')
    list_filter = ('status', 'type', "tariff", ('created_at', DateRangeFilter),)
    exclude = ('amount', 'amount_output', 'profit', 'admin_profit')
    readonly_fields = ('order_id_display', 'order_id', 'type', "tariff", 
                       'promocode', 'currency', 'exchange_course',
                       'input_amount', 'output_amount', 'profit_display', "admin_profit_display", "order_history",
                       "sum_of_transactions", "average_course", "sum_of_usdt") 
    inlines = [TransactionReceivingInline, TransactionSendingInline]

    def order_id_display(self, obj):
        html_content = format_html(
            '''
            <a href="#" onclick="copyToClipboard('{}'); return false;" 
            style="background-color: #4CAF50; color: white; padding: 5px 10px; text-align: center; text-decoration: none; display: inline-block; font-size: 14px; cursor: pointer; border-radius: 8px; transition: background-color 0.3s;">
            {}
            </a> 
            <div id="copyMessage" style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background-color: #4CAF50; color: white; padding: 10px 20px; border-radius: 5px; display: none; font-size: 14px;">
                Номер скопирован в буфер обмена!
            </div>
            <script type="text/javascript">
                function copyToClipboard(text) {{
                    const textarea = document.createElement('textarea');
                    textarea.value = text;
                    document.body.appendChild(textarea);
                    textarea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textarea);
                    
                    // Показываем сообщение
                    var message = document.getElementById('copyMessage');
                    message.style.display = 'block';
                    
                    // Скрываем сообщение через 2 секунды
                    setTimeout(function() {{
                        message.style.display = 'none';
                    }}, 2000);
                }}
            </script>
            ''',
            obj.order_id,
            obj.order_id,
        )
        
        return mark_safe(html_content) 
    order_id_display.short_description = "Номер заказа"

    def order_history(self, obj):
        """Отображает историю изменений заказа в виде таблицы с объектом изменения"""
        logs = LogEntry.objects.filter(
            content_type=ContentType.objects.get_for_model(Order),
            object_id=obj.id,
            action_flag=CHANGE
        ).select_related("user").order_by("-action_time")

        if not logs.exists():
            return "Изменений не найдено"

        rows = []
        for log in logs:
            time = localtime(log.action_time).strftime("%Y-%m-%d %H:%M:%S")
            user_link = format_html(
                '<a href="{}">{}</a>',
                reverse(f"admin:{User._meta.app_label}_{User._meta.model_name}_change", args=[log.user.id]),
                log.user.get_full_name() or log.user.username
            )

            object_repr = log.object_repr  

            changes = log.get_change_message()

            rows.append(
                f"<tr><td>{time}</td><td>{user_link}</td><td>{changes}</td><td>{object_repr}</td></tr>"
            )

        table_html = f"""
        <style>
            .history-table {{
                width: 100%;
                border-collapse: collapse;
            }}
            .history-table th, .history-table td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            .history-table th {{
                background-color: #f4f4f4;
            }}
        </style>
        <table class="history-table">
            <thead>
                <tr>
                    <th>Дата и время</th>
                    <th>Пользователь</th>
                    <th>Изменение</th>
                    <th>Объект</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """
        return mark_safe(table_html)

    order_history.short_description = "История изменений"

    def input_amount(self, obj):
        if obj.amount and obj.currency:
            return format_html(f'<span style="color: blue;">{obj.amount} {obj.currency.user_currency}</span>')
        elif obj.amount and not obj.currency:
            return format_html(f'<span style="color: blue;">{obj.amount}₽</span>')
        return "-"
    input_amount.admin_order_field = 'amount'
    input_amount.short_description = "Сумма"

    def output_amount(self, obj):
        if obj.amount and obj.currency:
            return format_html(f'<span style="color: blue;">{obj.amount_output} {obj.currency.exchange_currency}</span>')
        return "-"
    output_amount.admin_order_field = 'amount_output'
    output_amount.short_description = "К получению"

    def profit_display(self, obj=None):
        if obj.profit:
            return format_html(f'<span style="color: green;">{obj.profit }₽</span>')
        return "-"
    profit_display.short_description = "Прибыль"

    def admin_profit_display(self, obj=None):
        if obj.admin_profit:
            return format_html(f'<span style="color: green;">{obj.admin_profit }₽</span>')
        return "-"
    admin_profit_display.short_description = "Прибыль админа"

    def telegram(self, obj):
        return format_html('<a style="color: red;" href="https://t.me/{}">@{}</a>', obj.user.username, obj.user.username)
    telegram.admin_order_field = 'user__username'
    telegram.short_description = "Пользователь"

# транзакции
    def sum_of_transactions(self, obj=None):
        if obj:
            total_amount = obj.transactions_r.aggregate(Sum('amount'))['amount__sum']
            if total_amount:
                return format_html(f'<span style="color: blue;">{total_amount}</span>')
        return "-"
    sum_of_transactions.short_description = "Сумма транзакций"

    def average_course(self, obj=None):
        if obj:
            # Получаем среднее значение курса всех транзакций
            average_course = obj.transactions_r.aggregate(Avg('exchange_course'))['exchange_course__avg']
            if average_course:
                return format_html(f'<span style="color: blue;">{round(average_course, 2)}</span>')
        return "-"
    average_course.short_description = "Средний курс транзакций"

    def sum_of_usdt(self, obj=None):
            if obj:
                # Получаем сумму всех транзакций по USDT
                total_usdt = obj.transactions_r.aggregate(Sum('amount_usdt'))['amount_usdt__sum']
                if total_usdt:
                    return format_html(f'<span style="color: blue;">{round(total_usdt, 2)} USDT</span>')
            return "-"
    sum_of_usdt.short_description = "Сумма USDT"
# -------------
    def admin_display(self, obj):
        if obj.admin:
            user_link = format_html(
                    '<a href="{}">{}</a>',
                    reverse(f"admin:{User._meta.app_label}_{User._meta.model_name}_change", args=[obj.admin.id]),
                    obj.admin.username
                )
            return mark_safe(user_link)
        return "-"
    admin_display.admin_order_field = 'admin__username'
    admin_display.short_description = "Админ"

    def get_list_display(self, request):
        list_display = super().get_list_display(request)

        if not request.user.has_perm('orders.can_view_clean_course'):
            list_display = [field for field in list_display if field != "clean_course"]

        if not request.user.has_perm('orders.can_view_profit'):
            list_display = [field for field in list_display if (field != "profit_display" and field != "admin_profit_display")]

        return list_display

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)

        if not request.user.has_perm('orders.can_view_clean_course'):
            fields = [field for field in fields if field != "clean_course"]

        if not request.user.has_perm('orders.can_view_profit'):
            fields = [field for field in fields if (field != "profit_display" and field != "admin_profit_display")]

        return fields

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets = [
            (title, {"fields": list(fields["fields"])})
            if isinstance(fields, dict) else fields
            for title, fields in fieldsets
        ]

        if not request.user.has_perm('orders.can_view_clean_course'):
            for section in fieldsets:
                if "clean_course" in section[1]["fields"]:
                    section[1]["fields"].remove("clean_course")

        if not request.user.has_perm('orders.can_view_profit'):
            for section in fieldsets:
                if 'profit_display' in section[1]['fields']:
                    section[1]['fields'].remove('profit_display')
                if 'admin_profit_display' in section[1]['fields']:
                    section[1]['fields'].remove('admin_profit_display')

        return fieldsets