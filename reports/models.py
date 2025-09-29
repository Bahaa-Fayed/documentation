"""
Models for reports app - managing financial reports and analytics
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


class ReportTemplate(models.Model):
    """Report template model"""
    REPORT_TYPES = [
        ('income_statement', 'بيان الدخل'),
        ('balance_sheet', 'الميزانية العمومية'),
        ('cash_flow', 'تدفق النقد'),
        ('budget_variance', 'تباين الميزانية'),
        ('category_summary', 'ملخص التصنيفات'),
        ('monthly_summary', 'ملخص شهري'),
        ('yearly_summary', 'ملخص سنوي'),
        ('custom', 'مخصص'),
    ]
    
    FORMAT_TYPES = [
        ('html', 'HTML'),
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='اسم القالب')
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPES,
        verbose_name='نوع التقرير'
    )
    description = models.TextField(blank=True, null=True, verbose_name='وصف')
    
    # Report configuration
    chart_types = models.JSONField(default=list, verbose_name='أنواع الرسوم البيانية')
    date_range_days = models.PositiveIntegerField(default=30, verbose_name='نطاق التاريخ بالأيام')
    include_categories = models.JSONField(default=list, verbose_name='التصنيفات المضمنة')
    include_accounts = models.JSONField(default=list, verbose_name='الحسابات المضمنة')
    
    # Output format
    default_format = models.CharField(
        max_length=10,
        choices=FORMAT_TYPES,
        default='html',
        verbose_name='التنسيق الافتراضي'
    )
    
    # Public/Private settings
    is_public = models.BooleanField(default=False, verbose_name='عام')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    
    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0, verbose_name='عدد الاستخدام')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='أنشأ بواسطة'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'قالب تقرير'
        verbose_name_plural = 'قوالب التقارير'
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return self.name


class ScheduledReport(models.Model):
    """Scheduled report model"""
    FREQUENCY_TYPES = [
        ('daily', 'يومي'),
        ('weekly', 'أسبوعي'),
        ('monthly', 'شهري'),
        ('quarterly', 'ربعي'),
        ('yearly', 'سنوي'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('paused', 'متوقف'),
        ('completed', 'مكتمل'),
        ('failed', 'فشل'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المستخدم')
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        verbose_name='قالب التقرير'
    )
    name = models.CharField(max_length=200, verbose_name='اسم التقرير')
    
    # Scheduling
    frequency = models.CharField(
        max_length=15,
        choices=FREQUENCY_TYPES,
        verbose_name='التكرار'
    )
    day_of_week = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(6)],
        verbose_name='يوم الأسبوع'
    )
    day_of_month = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        verbose_name='يوم الشهر'
    )
    
    # Output configuration
    output_format = models.CharField(
        max_length=10,
        choices=ReportTemplate.FORMAT_TYPES,
        verbose_name='تنسيق المخرجات'
    )
    email_recipients = models.JSONField(default=list, verbose_name='متلقو البريد الإلكتروني')
    save_to_files = models.BooleanField(default=True, verbose_name='حفظ في الملفات')
    
    # Status and dates
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='الحالة'
    )
    last_run = models.DateTimeField(null=True, blank=True, verbose_name='آخر تشغيل')
    next_run = models.DateTimeField(null=True, blank=True, verbose_name='التشغيل التالي')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'تقرير مجدول'
        verbose_name_plural = 'التقارير المجدولة'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.frequency})"


class ReportExecution(models.Model):
    """Report execution model"""
    STATUS_CHOICES = [
        ('queued', 'في الطابور'),
        ('running', 'قيد التشغيل'),
        ('completed', 'مكتمل'),
        ('failed', 'فشل'),
    ]
    
    scheduled_report = models.ForeignKey(
        ScheduledReport,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='التقرير المجدول'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المستخدم')
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        verbose_name='قالب التقرير'
    )
    
    # Execution details
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='queued',
        verbose_name='الحالة'
    )
    parameters = models.JSONField(default=dict, verbose_name='المعاملات')
    
    # File information
    output_file = models.FileField(
        upload_to='reports/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name='ملف المخرجات'
    )
    output_format = models.CharField(
        max_length=10,
        choices=ReportTemplate.FORMAT_TYPES,
        verbose_name='تنسيق المخرجات'
    )
    
    # Execution metadata
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ البدء')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ الإتمام')
    execution_time = models.DurationField(null=True, blank=True, verbose_name='وقت التنفيذ')
    
    # Results
    record_count = models.PositiveIntegerField(null=True, blank=True, verbose_name='عدد السجلات')
    total_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='المجموع الإجمالي'
    )
    
    # Error handling
    error_message = models.TextField(null=True, blank=True, verbose_name='رسالة الخطأ')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'تنفيذ تقرير'
        verbose_name_plural = 'تنفيذات التقارير'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.template.name} - {self.status}"


class FinancialAnalytics(models.Model):
    """Financial analytics model"""
    METRIC_TYPES = [
        ('monthly_income', 'الدخل الشهري'),
        ('monthly_expenses', 'المصروفات الشهرية'),
        ('savings_rate', 'معدل الادخار'),
        ('expense_by_category', 'المصروفات حسب التصنيف'),
        ('income_vs_expense', 'الدخل مقابل المصروفات'),
        ('budget_performance', 'أداء الميزانية'),
        ('account_balance', 'رصيد الحساب'),
        ('debt_ratio', 'نسبة الدين'),
        ('investment_return', 'عائد الاستثمار'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المستخدم')
    metric_type = models.CharField(
        max_length=30,
        choices=METRIC_TYPES,
        verbose_name='نوع المقياس'
    )
    period_start = models.DateField(verbose_name='تاريخ بداية الفترة')
    period_end = models.DateField(verbose_name='تاريخ نهاية الفترة')


    value = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name='القيمة'
    )
    
    # Additional data for complex metrics
    breakdown_data = models.JSONField(
        default=dict,
        verbose_name='بيانات التفصيل'
    )
    chart_data = models.JSONField(
        default=dict,
        verbose_name='بيانات الرسم البياني'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'تحليل مالي'
        verbose_name_plural = 'التحليلات المالية'
        ordering = ['-created_at']
        unique_together = ['user', 'metric_type', 'period_start', 'period_end']
    
    def __str__(self):
        return f"{self.get_metric_type_display()} - {self.period_start} to {self.period_end}"