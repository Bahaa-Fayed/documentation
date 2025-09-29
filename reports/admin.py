"""
Admin configuration for reports app
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import ReportTemplate, ScheduledReport, ReportExecution, FinancialAnalytics


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'default_format', 'usage_count', 'is_public', 'is_active']
    list_filter = ['report_type', 'default_format', 'is_public', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['-usage_count', 'name']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('معلومات القالب', {
            'fields': ('name', 'report_type', 'description', 'created_by')
        }),
        ('إعدادات التقرير', {
            'fields': ('chart_types', 'date_range_days', 'include_categories', 'include_accounts')
        }),
        ('تنسيق المخرجات', {
            'fields': ('default_format',)
        }),
        ('الإعدادات العامة', {
            'fields': ('is_public', 'is_active')
        }),
        ('الإحصائيات', {
            'fields': ('usage_count', 'created_at', 'updated_at')
        }),
    )


@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'template', 'frequency', 'output_format', 'status', 'next_run', 'user'
    ]
    list_filter = ['frequency', 'output_format', 'status', 'template__report_type']
    search_fields = ['name', 'user__username']
    ordering = ['-created_at']
    readonly_fields = ['last_run', 'created_at']
    
    fieldsets = (
        ('معلومات التقرير المجدول', {
            'fields': ('user', 'template', 'name', 'status')
        }),
        ('جدولة التشغيل', {
            'fields': ('frequency', 'day_of_week', 'day_of_month')
        }),
        ('إعدادات المخرجات', {
            'fields': ('output_format', 'email_recipients', 'save_to_files')
        }),
        ('تواريخ التشغيل', {
            'fields': ('last_run', 'next_run', 'created_at')
        }),
    )


@admin.register(ReportExecution)
class ReportExecutionAdmin(admin.ModelAdmin):
    list_display = [
        'template', 'user', 'status', 'output_format', 'started_at', 'completed_at', 'execution_time'
    ]
    list_filter = ['status', 'output_format', 'template__report_type', 'started_at']
    search_fields = ['user__username', 'template__name']
    ordering = ['-created_at']
    readonly_fields = [
        'status', 'started_at', 'completed_at', 'execution_time',
        'record_count', 'total_amount', 'error_message', 'created_at'
    ]
    
    fieldsets = (
        ('معلومات التنفيذ', {
            'fields': ('scheduled_report', 'user', 'template', 'status')
        }),
        ('المعاملات والنتائج', {
            'fields': ('parameters', 'output_format', 'output_file')
        }),
        ('إحصائيات التنفيذ', {
            'fields': ('record_count', 'total_amount', 'execution_time'),
            'classes': ('collapse',)
        }),
        ('تواريخ التنفيذ', {
            'fields': ('started_at', 'completed_at', 'created_at')
        }),
        ('تتبع الأخطاء', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
    )


@admin.register(FinancialAnalytics)
class FinancialAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'metric_type', 'period_start', 'period_end', 'value_display', 'created_at'
    ]
    list_filter = ['metric_type', 'created_at']
    search_fields = ['user__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def value_display(self, obj):
        return f"{obj.value:,.2f}"
    value_display.short_description = "القيمة"
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('user', 'metric_type', 'period_start', 'period_end', 'value')
        }),
        ('البيانات التفصيلية', {
            'fields': ('breakdown_data', 'chart_data'),
            'classes': ('collapse',)
        }),
        ('التواريخ', {
            'fields': ('created_at',)
        }),
    )