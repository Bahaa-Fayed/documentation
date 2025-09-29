"""
Models for budgets app - managing budgets and financial goals
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal


class BudgetPeriod(models.Model):
    """Budget period model (monthly, yearly, etc.)"""
    PERIOD_TYPES = [
        ('monthly', 'شهري'),
        ('quarterly', 'ربعي'),
        ('yearly', 'سنوي'),
        ('custom', 'مخصص'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='اسم الفترة')
    period_type = models.CharField(
        max_length=10,
        choices=PERIOD_TYPES,
        verbose_name='نوع الفترة'
    )
    start_date = models.DateField(verbose_name='تاريخ البداية')
    end_date = models.DateField(verbose_name='تاريخ النهاية')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    
    class Meta:
        verbose_name = 'فترة ميزانية'
        verbose_name_plural = 'فترات الميزانيات'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"


class Budget(models.Model):
    """Budget model"""
    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('active', 'نشط'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
    ]
    
    ALERT_TYPES = [
        ('none', 'لا توجد تنبيهات'),
        ('80_percent', 'عند الوصول لـ 80%'),
        ('90_percent', 'عند الوصول لـ 90%'),
        ('100_percent', 'عند الوصول لـ 100%'),
        ('custom', 'مخصص'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المستخدم')
    name = models.CharField(max_length=200, verbose_name='اسم الميزانية')
    description = models.TextField(blank=True, null=True, verbose_name='وصف')
    
    # Budget period
    period = models.ForeignKey(
        BudgetPeriod,
        on_delete=models.CASCADE,
        verbose_name='فترة الميزانية'
    )
    
    # Budget categories
    categories = models.ManyToManyField(
        'categories.Category',
        through='BudgetCategory',
        verbose_name='التصنيفات'
    )
    
    # Total budget
    total_budget = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='مجموع الميزانية'
    )
    
    # Budget settings
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='الحالة'
    )
    alert_threshold = models.CharField(
        max_length=15,
        choices=ALERT_TYPES,
        default='90_percent',
        verbose_name='عتبة التنبيه'
    )
    custom_alert_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='نسبة التنبيه المخصصة'
    )
    
    # Financial tracking
    total_spent = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name='المجموع المنفق'
    )
    total_income = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name='مجموع الدخل'
    )
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ البدء')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ الإتمام')
    
    class Meta:
        verbose_name = 'ميزانية'
        verbose_name_plural = 'الميزانيات'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.period.name})"
    
    def get_spending_percentage(self):
        """Calculate spending percentage"""
        if self.total_budget == 0:
            return 0
        return (self.total_spent / self.total_budget) * 100
    
    def get_remaining_amount(self):
        """Get remaining budget amount"""
        return self.total_budget - self.total_spent
    
    def is_over_budget(self):
        """Check if budget is exceeded"""
        return self.total_spent > self.total_budget
    
    def get_status_color(self):
        """Get status color based on spending"""
        percentage = self.get_spending_percentage()
        if percentage >= 100:
            return '#dc3545'  # Red
        elif percentage >= 90:
            return '#fd7e14'  # Orange
        elif percentage >= 80:
            return '#ffc107'  # Yellow
        else:
            return '#28a745'  # Green
    
    def should_alert(self):
        """Check if alert should be triggered"""
        percentage = self.get_spending_percentage()
        
        if self.alert_threshold == '80_percent':
            return percentage >= 80
        elif self.alert_threshold == '90_percent':
            return percentage >= 90
        elif self.alert_threshold == '100_percent':
            return percentage >= 100
        elif self.alert_threshold == 'custom':
            return percentage >= self.custom_alert_percentage
        
        return False


class BudgetCategory(models.Model):
    """Budget category details"""
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, verbose_name='الميزانية')
    category = models.ForeignKey(
        'categories.Category', 
        on_delete=models.CASCADE, 
        verbose_name='التصنيف'
    )
    allocated_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='المبلغ المخصص'
    )
    spent_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name='المبلغ المنفق'
    )
    
    class Meta:
        verbose_name = 'تصنيف ميزانية'
        verbose_name_plural = 'تصنيفات الميزانية'
        unique_together = ['budget', 'category']
    
    def __str__(self):
        return f"{self.budget.name} - {self.category.name}"
    
    def get_spending_percentage(self):
        """Calculate category spending percentage"""
        if self.allocated_amount == 0:
            return 0
        return (self.spent_amount / self.allocated_amount) * 100
    
    def get_remaining_amount(self):
        """Get remaining budget for category"""
        return self.allocated_amount - self.spent_amount
    
    def is_over_budget(self):
        """Check if category budget is exceeded"""
        return self.spent_amount > self.allocated_amount


class BudgetAlert(models.Model):
    """Budget alert model"""
    ALERT_TYPES = [
        ('budget_threshold', 'تجاوز عتبة الميزانية'),
        ('category_threshold', 'تجاوز عتبة التصنيف'),
        ('low_funds', 'نفاد الأموال'),
        ('achievement', 'إنجاز هدف'),
    ]
    
    STATUS_CHOICES = [
        ('unread', 'غير مقروء'),
        ('read', 'مقروء'),
        ('acknowledged', 'معترف به'),
    ]
    
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        verbose_name='الميزانية'
    )
    budget_category = models.ForeignKey(
        BudgetCategory,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='تصنيف الميزانية'
    )
    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPES,
        verbose_name='نوع التنبيه'
    )
    title = models.CharField(max_length=200, verbose_name='عنوان التنبيه')
    message = models.TextField(verbose_name='رسالة التنبيه')
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='unread',
        verbose_name='الحالة'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'تنبيه ميزانية'
        verbose_name_plural = 'تنبيهات الميزانية'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.budget.name}"


class BudgetTemplate(models.Model):
    """Template for quick budget creation"""
    name = models.CharField(max_length=200, verbose_name='اسم القالب')
    description = models.TextField(blank=True, null=True, verbose_name='وصف')
    categories_data = models.JSONField(verbose_name='بيانات التصنيفات')
    total_budget = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name='مجموع الميزانية'
    )
    period_type = models.CharField(
        max_length=10,
        choices=BudgetPeriod.PERIOD_TYPES,
        default='monthly',
        verbose_name='نوع الفترة'
    )
    is_public = models.BooleanField(default=True, verbose_name='عمومي')
    usage_count = models.PositiveIntegerField(default=0, verbose_name='عدد الاستخدام')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='أنشأ بواسطة'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'قالب ميزانية'
        verbose_name_plural = 'قوالب الميزانيات'
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.total_budget:,.2f})"