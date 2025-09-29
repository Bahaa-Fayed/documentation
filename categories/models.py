"""
Models for the categories app - managing income and expense categories
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from colorfield.fields import ColorField


class Category(models.Model):
    """Category model for transactions"""
    CATEGORY_TYPES = [
        ('income', 'دخل'),
        ('expense', 'مصروف'),
        ('transfer', 'تحويل'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name='المستخدم'
    )
    name = models.CharField(max_length=200, verbose_name='اسم التصنيف')
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='children',
        verbose_name='التصنيف الأب'
    )
    category_type = models.CharField(
        max_length=10,
        choices=CATEGORY_TYPES,
        verbose_name='نوع التصنيف'
    )
    color = ColorField(default='#007bff', verbose_name='لون التصنيف')
    icon = models.CharField(
        max_length=100, 
        default='fas fa-folder',
        verbose_name='أيقونة التصنيف'
    )
    description = models.TextField(blank=True, null=True, verbose_name='وصف')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    sort_order = models.PositiveIntegerField(default=0, verbose_name='ترتيب')
    budget_limit = models.DecimalField(
        max_digits=18, 
        decimal_places=2,
        null=True, 
        blank=True,
        verbose_name='حد الميزانية الشهرية'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'تصنيف'
        verbose_name_plural = 'التصنيفات'
        ordering = ['sort_order', 'name']
        unique_together = ['user', 'name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} - {self.name}"
        return self.name
    
    def get_full_path(self):
        """Get full category path as string"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name
    
    def get_children_count(self):
        """Get number of child categories"""
        return self.children.filter(is_active=True).count()
    
    def get_monthly_spending(self, year, month):
        """Get monthly spending for this category"""
        from transactions.models import Transaction
        return Transaction.objects.filter(
            category=self,
            date__year=year,
            date__month=month,
            transaction_type='expense'
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
    
    def is_over_budget(self, year, month):
        """Check if category spending exceeds budget limit"""
        if not self.budget_limit:
            return False
        
        monthly_spending = self.get_monthly_spending(year, month)
        return monthly_spending > self.budget_limit


class CategoryTemplate(models.Model):
    """Templates for quick category creation"""
    name = models.CharField(max_length=200, verbose_name='اسم التصنيف')
    parent_name = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name='اسم التصنيف الأب'
    )
    category_type = models.CharField(
        max_length=10,
        choices=Category.CATEGORY_TYPES,
        verbose_name='نوع التصنيف'
    )
    color = ColorField(default='#007bff', verbose_name='لون التصنيف')
    icon = models.CharField(
        max_length=100, 
        default='fas fa-folder',
        verbose_name='أيقونة التصنيف'
    )
    description = models.TextField(blank=True, null=True, verbose_name='وصف')
    budget_limit = models.DecimalField(
        max_digits=18, 
        decimal_places=2,
        null=True, 
        blank=True,
        verbose_name='حد الميزانية الشهرية'
    )
    is_public = models.BooleanField(default=True, verbose_name='عمومي')
    sort_order = models.PositiveIntegerField(default=0, verbose_name='ترتيب')
    usage_count = models.PositiveIntegerField(default=0, verbose_name='عدد الاستخدام')
    
    class Meta:
        verbose_name = 'قالب تصنيف'
        verbose_name_plural = 'قوالب التصنيفات'
        ordering = ['sort_order', 'name']
        unique_together = ['name', 'parent_name']
    
    def __str__(self):
        if self.parent_name:
            return f"{self.parent_name} - {self.name}"
        return self.name