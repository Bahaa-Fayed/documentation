"""
Models for goals app - managing financial goals and targets
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal


class FinancialGoal(models.Model):
    """Financial goal model"""
    GOAL_TYPES = [
        ('savings', 'ادخار'),
        ('debt_payment', 'سداد دين'),
        ('investment', 'استثمار'),
        ('major_purchase', 'شراء كبير'),
        ('emergency_fund', 'صندوق الطوارئ'),
        ('education', 'تعليم'),
        ('retirement', 'تقاعد'),
        ('travel', 'سفر'),
        ('wedding', 'زفاف'),
        ('other', 'أخرى'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('completed', 'مكتمل'),
        ('paused', 'متوقف'),
        ('cancelled', 'ملغي'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'منخفض'),
        ('medium', 'متوسط'),
        ('high', 'مرتفع'),
        ('critical', 'حرج'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المستخدم')
    name = models.CharField(max_length=200, verbose_name='اسم الهدف')
    description = models.TextField(blank=True, null=True, verbose_name='وصف')
    
    # Goal type and priority
    goal_type = models.CharField(
        max_length=20,
        choices=GOAL_TYPES,
        verbose_name='نوع الهدف'
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name='الأولوية'
    )
    
    # Financial targets
    target_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='المبلغ المستهدف'
    )
    current_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name='المبلغ الحالي'
    )
    
    # Timeline
    start_date = models.DateField(default=timezone.now, verbose_name='تاريخ البداية')
    target_date = models.DateField(verbose_name='التاريخ المستهدف')
    completed_date = models.DateField(null=True, blank=True, verbose_name='تاريخ الإتمام')
    
    # Status and tracking
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='الحالة'
    )
    monthly_target = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='الهدف الشهري'
    )
    
    # Associated accounts
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='الحساب المرتبط'
    )
    
    # Colors and icons
    color = models.CharField(max_length=7, default='#ffc107', verbose_name='لون الهدف')
    icon = models.CharField(max_length=100, default='fas fa-target', verbose_name='أيقونة الهدف')
    
    # Additional information
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='التصنيف المرتبط'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'هدف مالي'
        verbose_name_plural = 'الأهداف المالية'
        ordering = ['priority', 'target_date']
    
    def __str__(self):
        return f"{self.name} - {self.current_amount:,.2f}/{self.target_amount:,.2f}"
    
    def get_progress_percentage(self):
        """Calculate progress percentage"""
        if self.target_amount == 0:
            return 0
        return (self.current_amount / self.target_amount) * 100
    
    def get_remaining_amount(self):
        """Get remaining amount to reach goal"""
        return self.target_amount - self.current_amount
    
    def get_days_remaining(self):
        """Get days remaining to reach target date"""
        today = timezone.now().date()
        return (self.target_date - today).days
    
    def get_monthly_progress_needed(self):
        """Calculate monthly progress needed to reach goal"""
        days_remaining = self.get_days_remaining()
        if days_remaining <= 0:
            return self.get_remaining_amount()
        
        months_remaining = days_remaining / 30.44  # Average days per month
        return self.get_remaining_amount() / max(months_remaining, 1)
    
    def get_progress_status(self):
        """Get progress status with color"""
        percentage = self.get_progress_percentage()
        if percentage >= 100:
            return {'status': 'completed', 'color': '#28a745'}
        elif percentage >= 75:
            return {'status': 'on_track', 'color': '#17a2b8'}
        elif percentage >= 50:
            return {'status': 'progress', 'color': '#ffc107'}
        elif percentage >= 25:
            return {'status': 'starting', 'color': '#fd7e14'}
        else:
            return {'status': 'behind', 'color': '#dc3545'}
    
    def is_behind_schedule(self):
        """Check if goal is behind schedule"""
        expected_amount = self.get_monthly_progress_needed() * 12
        return self.current_amount < (expected_amount * 0.8)  # 80% threshold


class GoalContribution(models.Model):
    """Goal contribution model"""
    CONTRIBUTION_TYPES = [
        ('manual', 'يدوي'),
        ('automatic', 'تلقائي'),
        ('transaction', 'من معاملة'),
        ('transfer', 'تحويل'),
    ]
    
    goal = models.ForeignKey(
        FinancialGoal,
        on_delete=models.CASCADE,
        related_name='contributions',
        verbose_name='الهدف'
    )
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='المبلغ'
    )
    contribution_type = models.CharField(
        max_length=15,
        choices=CONTRIBUTION_TYPES,
        default='manual',
        verbose_name='نوع المساهمة'
    )
    
    # Source information
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        verbose_name='الحساب المصدر'
    )
    transaction = models.ForeignKey(
        'transactions.Transaction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='المعاملة المرتبطة'
    )
    
    # Additional information
    description = models.TextField(blank=True, null=True, verbose_name='وصف')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    
    # Timestamps
    contribution_date = models.DateTimeField(default=timezone.now, verbose_name='تاريخ المساهمة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'مساهمة في هدف'
        verbose_name_plural = 'مساهمات الأهداف'
        ordering = ['-contribution_date']
    
    def __str__(self):
        return f"{self.goal.name} - {self.amount:,.2f} ({self.contribution_date.strftime('%Y-%m-%d')})"


class GoalMilestone(models.Model):
    """Goal milestone model"""
    milestone = models.ForeignKey(
        FinancialGoal,
        on_delete=models.CASCADE,
        related_name='milestones',
        verbose_name='المعالم'
    )
    name = models.CharField(max_length=200, verbose_name='اسم المعلم')
    target_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name='المبلغ المستهدف للمعلم'
    )
    target_date = models.DateField(verbose_name='التاريخ المستهدف')
    description = models.TextField(blank=True, null=True, verbose_name='وصف')
    
    # Status tracking
    is_achieved = models.BooleanField(default=False, verbose_name='محقق')
    achieved_date = models.DateField(null=True, blank=True, verbose_name='تاريخ الإنجاز')
    
    # Additional information
    reward_description = models.TextField(blank=True, null=True, verbose_name='وصف المكافأة')
    color = models.CharField(max_length=7, default='#6f42c1', verbose_name='لون المعلم')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'معلم هدف'
        verbose_name_plural = 'معالم الأهداف'
        ordering = ['target_amount', 'target_date']
    
    def __str__(self):
        return f"{self.milestone.name} - {self.name} ({self.target_amount:,.2f})"


class GoalTemplate(models.Model):
    """Goal template model"""
    name = models.CharField(max_length=200, verbose_name='اسم القالب')
    description = models.TextField(blank=True, null=True, verbose_name='وصف')
    
    # Template configuration
    goal_type = models.CharField(
        max_length=20,
        choices=FinancialGoal.GOAL_TYPES,
        verbose_name='نوع الهدف'
    )
    priority = models.CharField(
        max_length=10,
        choices=FinancialGoal.PRIORITY_CHOICES,
        default='medium',
        verbose_name='الأولوية'
    )
    default_duration_months = models.PositiveIntegerField(default=12, verbose_name='المدة الافتراضية بالأشهر')
    
    # Visual settings
    color = models.CharField(max_length=7, default='#ffc107', verbose_name='اللون')
    icon = models.CharField(max_length=100, default='fas fa-target', verbose_name='الأيقونة')
    
    # Public settings
    is_public = models.BooleanField(default=True, verbose_name='عام')
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
        verbose_name = 'قالب هدف'
        verbose_name_plural = 'قوالب الأهداف'
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return self.name