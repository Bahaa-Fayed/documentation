"""
Admin configuration for transactions app
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.admin import SimpleListFilter
from django.utils import timezone
from .models import Transaction, TransactionTag, TransactionAttachment, TransactionTemplate, TransactionComment


class TransactionTypeFilter(SimpleListFilter):
    title = 'نوع المعاملة'
    parameter_name = 'transaction_type'
    
    def lookups(self, request, model_admin):
        return (
            ('income', 'دخل'),
            ('expense', 'مصروف'),
            ('transfer', 'تحويل'),
        )
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(transaction_type=self.value())


class DateRangeFilter(SimpleListFilter):
    title = 'نطاق التاريخ'
    parameter_name = 'date_range'
    
    def lookups(self, request, model_admin):
        return (
            ('today', 'اليوم'),
            ('week', 'هذا الأسبوع'),
            ('month', 'هذا الشهر'),
            ('year', 'هذا العام'),
            ('last_month', 'الشهر الماضي'),
            ('last_year', 'العام الماضي'),
        )
    
    def queryset(self, request, queryset):
        now = timezone.now()
        
        if self.value() == 'today':
            return queryset.filter(date__date=now.date())
        elif self.value() == 'week':
            start_of_week = now - timezone.timedelta(days=now.weekday())
            return queryset.filter(date__gte=start_of_week.date())
        elif self.value() == 'month':
            return queryset.filter(date__year=now.year, date__month=now.month)
        elif self.value() == 'year':
            return queryset.filter(date__year=now.year)
        elif self.value() == 'last_month':
            last_month = now.month - 1 if now.month > 1 else 12
            last_year = now.year if now.month > 1 else now.year - 1
            return queryset.filter(date__year=last_year, date__month=last_month)
        elif self.value() == 'last_year':
            return queryset.filter(date__year=now.year - 1)


class TransactionAttachmentInline(admin.TabularInline):
    model = TransactionAttachment
    extra = 0
    readonly_fields = ['file_size', 'uploaded_at']
    fields = ['file', 'original_filename', 'file_type', 'file_size', 'description', 'uploaded_at']


class TransactionCommentInline(admin.TabularInline):
    model = TransactionComment
    extra = 0
    readonly_fields = ['created_at', 'updated_at']
    fields = ['user', 'content', 'created_at', 'updated_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'id_short', 'transaction_type_display', 'amount_display', 'account', 'category',
        'date', 'status', 'user', 'created_at'
    ]
    list_filter = [TransactionTypeFilter, DateRangeFilter, 'status', 'is_recurring', 'user']
    search_fields = ['description', 'notes', 'account__name', 'category__name']
    ordering = ['-date', '-created_at']
    readonly_fields = ['id', 'balance_after', 'effective_amount', 'created_at', 'updated_at']
    
    inlines = [TransactionAttachmentInline, TransactionCommentInline]
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('id', 'user', 'transaction_type', 'amount', 'effective_amount', 'status')
        }),
        ('الحساب والتصنيف', {
            'fields': ('account', 'category')
        }),
        ('التفاصيل', {
            'fields': ('description', 'date', 'location', 'notes')
        }),
        ('العلامات والمرفقات', {
            'fields': ('tags',)
        }),
        ('المعاملة المتكررة', {
            'fields': ('is_recurring', 'recurrence_type', 'recurrence_interval', 'recurrence_end_date'),
            'classes': ('collapse',)
        }),
        ('التتبع المالي', {
            'fields': ('balance_after',),
            'classes': ('collapse',)
        }),
        ('نظام', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = "المعرف"
    
    def transaction_type_display(self, obj):
        colors = {
            'income': '#28a745',
            'expense': '#dc3545',
            'transfer': '#007bff'
        }
        color = colors.get(obj.transaction_type, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_transaction_type_display()
        )
    transaction_type_display.short_description = "النوع"
    
    def amount_display(self, obj):
        amount_str = f"{obj.amount:,.2f}"
        if obj.transaction_type == 'expense':
            return format_html('<span style="color: #dc3545;">-{}</span>', amount_str)
        elif obj.transaction_type == 'income':
            return format_html('<span style="color: #28a745;">+{}</span>', amount_str)
        return amount_str
    amount_display.short_description = "المبلغ"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'account', 'category', 'created_by'
        ).prefetch_related('tags', 'attachments')


@admin.register(TransactionTag)
class TransactionTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_display', 'usage_count']
    list_filter = ['usage_count']
    search_fields = ['name', 'description']
    ordering = ['-usage_count', 'name']
    
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 3px 8px; border-radius: 3px; color: white;">{}</span>',
            obj.color,
            obj.name
        )
    color_display.short_description = "العلامة"


@admin.register(TransactionTemplate)
class TransactionTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'transaction_type', 'amount', 'account', 'usage_count', 'is_active']
    list_filter = ['transaction_type', 'is_active', 'account__account_type']
    search_fields = ['name', 'description']
    ordering = ['-usage_count', 'name']
    readonly_fields = ['usage_count', 'created_at']


@admin.register(TransactionComment)
class TransactionCommentAdmin(admin.ModelAdmin):
    list_display = ['transaction_short', 'user', 'content_short', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'user__username', 'transaction__description']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def transaction_short(self, obj):
        return f"{obj.transaction.id} - {obj.transaction.description[:50]}"
    transaction_short.short_description = "المعاملة"
    
    def content_short(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_short.short_description = "المحتوى"