"""
Admin configuration for accounts app
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Currency, Account, AccountTransfer, AccountTemplate


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol', 'exchange_rate', 'is_primary', 'is_active']
    list_filter = ['is_primary', 'is_active']
    search_fields = ['code', 'name']
    ordering = ['code']
    actions = ['make_active', 'make_inactive']
    
    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "تفعيل العملات المحددة"
    
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "إلغاء تفعيل العملات المحددة"


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'account_type', 'currency', 'balance_display', 'is_active', 'created_at']
    list_filter = ['account_type', 'currency', 'is_active', 'created_at']
    search_fields = ['name', 'owner__username']
    ordering = ['name']
    readonly_fields = ['current_balance', 'created_at', 'updated_at']
    list_editable = ['is_active']
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('owner', 'name', 'account_type', 'currency', 'description')
        }),
        ('التوازن', {
            'fields': ('initial_balance', 'current_balance')
        }),
        ('التنسيق', {
            'fields': ('color', 'icon')
        }),
        ('الحالة', {
            'fields': ('is_active',)
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def balance_display(self, obj):
        return f"{obj.current_balance:,.2f} {obj.currency.symbol}"
    balance_display.short_description = "الرصيد الحالي"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner', 'currency')


class AccountTransferInline(admin.TabularInline):
    model = AccountTransfer
    extra = 0
    readonly_fields = ['converted_amount', 'created_at']
    
    fields = ['from_account', 'to_account', 'amount', 'exchange_rate', 'converted_amount', 'description', 'transfer_date']


@admin.register(AccountTransfer)
class AccountTransferAdmin(admin.ModelAdmin):
    list_display = ['transfer_display', 'user', 'amount_display', 'transfer_date', 'created_at']
    list_filter = ['transfer_date', 'created_at']
    search_fields = ['from_account__name', 'to_account__name', 'user__username']
    readonly_fields = ['converted_amount', 'created_at']
    ordering = ['-transfer_date']
    
    def transfer_display(self, obj):
        return f"{obj.from_account.name} → {obj.to_account.name}"
    transfer_display.short_description = "التحويل"
    
    def amount_display(self, obj):
        return f"{obj.amount:,.2f} {obj.from_account.currency.symbol}"
    amount_display.short_description = "المبلغ"


@admin.register(AccountTemplate)
class AccountTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'account_type', 'default_currency', 'is_public', 'created_by']
    list_filter = ['account_type', 'default_currency', 'is_public']
    search_fields = ['name']
    ordering = ['name']
    readonly_fields = ['created_by']


@admin.action(description="إعادة حساب رصيد الحسابات")
def recalculate_balances(modeladmin, request, queryset):
    """Recalculate account balances"""
    for account in queryset:
        # Calculate balance from transactions
        from transactions.models import Transaction
        transactions = Transaction.objects.filter(account=account, status='completed')
        total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
        total_expense = sum(t.amount for t in transactions if t.transaction_type == 'expense')
        account.current_balance = account.initial_balance + total_income - total_expense
        account.save()


# Add the action to AccountAdmin
AccountAdmin.actions = [recalculate_balances]