"""
Admin configuration for budgets app
"""

from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter
from django.utils import timezone
from django.db import models
from decimal import Decimal
import calendar
from .models import BudgetPeriod, Budget, BudgetCategory, BudgetAlert, BudgetTemplate


class BudgetStatusFilter(SimpleListFilter):
    title = 'حالة الميزانية'
    parameter_name = 'budget_status'
    
    def lookups(self, request, model_admin):
        return (
            ('over_budget', 'تجاوز الميزانية'),
            ('near_limit', 'بالقرب من الحد'),
            ('on_track', 'على المسار الصحيح'),
            ('under_spent', 'أقل من المتوقع'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'over_budget':
            return queryset.filter(total_spent__gt=models.F('total_budget'))
        elif self.value() == 'near_limit':
            return queryset.filter(total_spent__gte=models.F('total_budget') * Decimal('0.9'))
        elif self.value() == 'on_track':
            return queryset.filter(
                total_spent__lt=models.F('total_budget') * Decimal('0.9'),
                total_spent__gt=models.F('total_budget') * Decimal('0.5')
            )
        elif self.value() == 'under_spent':
            return queryset.filter(total_spent__lt=models.F('total_budget') * Decimal('0.5'))


class BudgetCategoryInline(admin.TabularInline):
    model = BudgetCategory
    extra = 0
    fields = ['category', 'allocated_amount', 'spent_amount', 'get_spending_percentage_display']
    readonly_fields = ['get_spending_percentage_display']
    
    def get_spending_percentage_display(self, obj):
        if obj.pk:
            percentage = obj.get_spending_percentage()
            color = '#dc3545' if percentage > 100 else '#ffc107' if percentage > 90 else '#28a745'
            return format_html(
                '<span style="color: {};">{:.1f}%</span>',
                color,
                percentage
            )
        return '-'
        get_spending_percentage_display.short_description = "نسبة الإنفاق"


@admin.register(BudgetPeriod)
class BudgetPeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'period_type', 'start_date', 'end_date', 'duration_days', 'is_active']
    list_filter = ['period_type', 'is_active']
    search_fields = ['name']
    ordering = ['-start_date']
    
    def duration_days(self, obj):
        return (obj.end_date - obj.start_date).days
    duration_days.short_description = "المدة بالأيام"


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'status', 'total_budget_display', 'total_spent_display',
        'progress_bar', 'alert_threshold', 'user', 'period'
    ]
    list_filter = [BudgetStatusFilter, 'status', 'alert_threshold', 'user', 'period__period_type']
    search_fields = ['name', 'description', 'user__username']
    ordering = ['-created_at']
    readonly_fields = ['total_spent', 'total_income', 'created_at', 'updated_at', 'started_at', 'completed_at']
    
    inlines = [BudgetCategoryInline]
    
    fieldsets = (
        ('معلومات الميزانية', {
            'fields': ('user', 'name', 'description', 'status')
        }),
        ('الفترة', {
            'fields': ('period',)
        }),
        ('المبالغ', {
            'fields': ('total_budget', 'total_spent', 'total_income')
        }),
        ('إعدادات التنبيه', {
            'fields': ('alert_threshold', 'custom_alert_percentage'),
            'classes': ('collapse',)
        }),
        ('التواريخ', {
            'fields': ('started_at', 'completed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_budget_display(self, obj):
        return f"{obj.total_budget:,.2f}"
    total_budget_display.short_description = "إجمالي الميزانية"
    
    def total_spent_display(self, obj):
        return f"{obj.total_spent:,.2f}"
    total_spent_display.short_description = "المجموع المنفق"
    
    def progress_bar(self, obj):
        percentage = obj.get_spending_percentage()
        remaining_percentage = min(100 - percentage, 100)
        
        color = obj.get_status_color()
        
        progress_html = '''
            <div style="width: 100px; height: 20px; border: 1px solid #ccc; background-color: #f0f0f0; position: relative;">
                <div style="width: {}%; height: 100%; background-color: {}; position: absolute; top: 0; left: 0;"></div>
                <div style="width: {}%; height: 100%; background-color: #e9ecef; position: absolute; top: 0; right: 0;"></div>
            </div>
        '''.format(percentage, color, remaining_percentage)
        
        return format_html('<div>{}</div><small>{:.1f}%</small>', progress_html, percentage)
    progress_bar.short_description = "التقدم"


@admin.register(BudgetAlert)
class BudgetAlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'budget', 'alert_type', 'status', 'created_at']
    list_filter = ['alert_type', 'status', 'created_at']
    search_fields = ['title', 'message', 'budget__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('budget', 'budget_category')


@admin.register(BudgetTemplate)
class BudgetTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_budget', 'period_type', 'usage_count', 'is_public', 'created_by']
    list_filter = ['period_type', 'is_public']
    search_fields = ['name', 'description']
    ordering = ['-usage_count', 'name']
    readonly_fields = ['usage_count', 'created_at']
    
    fieldsets = (
        ('معلومات القالب', {
            'fields': ('name', 'description', 'is_public', 'created_by')
        }),
        ('إعدادات الميزانية', {
            'fields': ('categories_data', 'total_budget', 'period_type')
        }),
        ('الإحصائيات', {
            'fields': ('usage_count', 'created_at')
        }),
    )