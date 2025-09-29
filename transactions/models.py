"""
Models for transactions app - managing income and expense transactions
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.urls import reverse
from decimal import Decimal
import uuid


class Transaction(models.Model):
    """Transaction model"""
    TRANSACTION_TYPES = [
        ('income', 'دخل'),
        ('expense', 'مصروف'),
        ('transfer', 'تحويل'),
    ]
    
    RECURRENCE_TYPES = [
        ('none', 'للمرة الواحدة'),
        ('daily', 'يومي'),
        ('weekly', 'أسبوعي'),
        ('monthly', 'شهري'),
        ('yearly', 'سنوي'),
        ('custom', 'مخصص'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'في الانتظار'),
        ('completed', 'مكتمل'),
        ('failed', 'فشل'),
        ('cancelled', 'ملغي'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المستخدم')
    
    # Basic transaction details
    amount = models.DecimalField(
        max_digits=18, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='المبلغ'
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES,
        verbose_name='نوع المعاملة'
    )
    
    # Account information
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        verbose_name='الحساب'
    )
    
    # Category information
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='التصنيف'
    )
    
    # Transaction metadata
    description = models.TextField(blank=True, null=True, verbose_name='وصف')
    date = models.DateTimeField(default=timezone.now, verbose_name='التاريخ والوقت')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='completed',
        verbose_name='الحالة'
    )
    
    # Tags
    tags = models.ManyToManyField(
        'TransactionTag',
        blank=True,
        verbose_name='العلامات'
    )
    
    # Attachments - Note: attachments handled separately via foreign key
    
    # Recurring transaction
    is_recurring = models.BooleanField(default=False, verbose_name='معاملة متكررة')
    recurrence_type = models.CharField(
        max_length=10,
        choices=RECURRENCE_TYPES,
        default='none',
        verbose_name='نوع التكرار'
    )
    recurrence_interval = models.PositiveIntegerField(
        default=1,
        verbose_name='فترة التكرار'
    )
    recurrence_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='تاريخ انتهاء التكرار'
    )
    
    # Financial tracking
    balance_after = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='الرصيد بعد المعاملة'
    )
    
    # Additional information
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name='الموقع')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_transactions',
        verbose_name='أنشأ بواسطة'
    )
    
    # Financial calculations
    effective_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name='المبلغ الفعلي'
    )
    
    class Meta:
        verbose_name = 'معاملة'
        verbose_name_plural = 'المعاملات'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'transaction_type']),
            models.Index(fields=['account', 'date']),
            models.Index(fields=['category', 'date']),
        ]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} - {self.date.strftime('%Y-%m-%d')}"
    
    def save(self, *args, **kwargs):
        """Calculate effective amount and update account balance"""
        # Set effective amount
        if self.transaction_type == 'expense':
            self.effective_amount = -self.amount
        else:
            self.effective_amount = self.amount
        
        # Update account balance
        self.account.update_balance(self.amount, self.transaction_type)
        self.balance_after = self.account.current_balance
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Get absolute URL for the transaction"""
        return reverse('transactions:transaction_detail', kwargs={'pk': self.pk})
    
    def get_effective_amount_display(self):
        """Get formatted effective amount"""
        sign = '+' if self.effective_amount >= 0 else '-'
        return f"{sign}{abs(self.effective_amount):,.2f}"


class TransactionTag(models.Model):
    """Tag model for transactions"""
    name = models.CharField(max_length=100, unique=True, verbose_name='اسم العلامة')
    color = models.CharField(max_length=7, default='#6c757d', verbose_name='لون العلامة')
    description = models.TextField(blank=True, null=True, verbose_name='وصف')
    usage_count = models.PositiveIntegerField(default=0, verbose_name='عدد الاستخدام')
    
    class Meta:
        verbose_name = 'علامة معاملة'
        verbose_name_plural = 'علامات المعاملات'
        ordering = ['name']
    
    def __str__(self):
        return f"#{self.name}"


class TransactionAttachment(models.Model):
    """Attachment model for transaction documents"""
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='transaction_attachments',
        verbose_name='المعاملة'
    )
    file = models.FileField(
        upload_to='transaction_attachments/%Y/%m/%d/',
        verbose_name='الملف'
    )
    file_type = models.CharField(max_length=50, verbose_name='نوع الملف')
    file_size = models.PositiveIntegerField(verbose_name='حجم الملف')
    original_filename = models.CharField(max_length=255, verbose_name='اسم الملف الأصلي')
    description = models.TextField(blank=True, null=True, verbose_name='وصف')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الرفع')
    
    class Meta:
        verbose_name = 'مرفق معاملة'
        verbose_name_plural = 'مرفقات المعاملات'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.original_filename} - {self.transaction.id}"


class TransactionTemplate(models.Model):
    """Template model for frequently used transactions"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='المستخدم'
    )
    name = models.CharField(max_length=200, verbose_name='اسم القالب')
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='المبلغ'
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=Transaction.TRANSACTION_TYPES,
        verbose_name='نوع المعاملة'
    )
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        verbose_name='الحساب'
    )
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='التصنيف'
    )
    description = models.TextField(blank=True, null=True, verbose_name='وصف')
    tags = models.ManyToManyField(
        TransactionTag,
        blank=True,
        verbose_name='العلامات'
    )
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    usage_count = models.PositiveIntegerField(default=0, verbose_name='عدد الاستخدام')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'قالب معاملة'
        verbose_name_plural = 'قوالب المعاملات'
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_transaction_type_display()})"


class TransactionComment(models.Model):
    """Comment model for transactions"""
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='المعاملة'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المستخدم')
    content = models.TextField(verbose_name='المحتوى')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'تعليق'
        verbose_name_plural = 'التعليقات'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"تعليق من {self.user.username} على {self.transaction.id}"