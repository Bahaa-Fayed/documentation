"""
Models for the accounts app - managing accounts and transfers
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


class AccountType(models.TextChoices):
    """Account type choices"""
    SAVINGS = 'savings', 'حساب توفير'
    CURRENT = 'current', 'حساب جاري'
    CREDIT = 'credit', 'حساب ائتمان'
    CASH = 'cash', 'نقد'
    INVESTMENT = 'investment', 'استثمار'
    DEBT = 'debt', 'دين'
    OTHER = 'other', 'أخرى'


class Currency(models.Model):
    """Currency model"""
    code = models.CharField(max_length=3, unique=True, verbose_name='رمز العملة')
    name = models.CharField(max_length=100, verbose_name='اسم العملة')
    symbol = models.CharField(max_length=10, verbose_name='رمز العملة')
    exchange_rate = models.DecimalField(
        max_digits=18, 
        decimal_places=8, 
        default=1.0,
        verbose_name='سعر الصرف'
    )
    is_primary = models.BooleanField(default=False, verbose_name='عملة أساسية')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    
    class Meta:
        verbose_name = 'عملة'
        verbose_name_plural = 'العملات'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Account(models.Model):
    """Account model for managing different accounts"""
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المالك')
    name = models.CharField(max_length=200, verbose_name='اسم الحساب')
    account_type = models.CharField(
        max_length=20, 
        choices=AccountType.choices,
        default=AccountType.CURRENT,
        verbose_name='نوع الحساب'
    )
    currency = models.ForeignKey(
        Currency, 
        on_delete=models.CASCADE,
        verbose_name='العملة'
    )
    initial_balance = models.DecimalField(
        max_digits=18, 
        decimal_places=2,
        default=0,
        verbose_name='الرصيد الابتدائي'
    )
    current_balance = models.DecimalField(
        max_digits=18, 
        decimal_places=2,
        default=0,
        verbose_name='الرصيد الحالي'
    )
    description = models.TextField(blank=True, null=True, verbose_name='وصف')
    color = models.CharField(
        max_length=7, 
        default='#007bff',
        verbose_name='لون الحساب'
    )
    icon = models.CharField(
        max_length=100, 
        default='fas fa-wallet',
        verbose_name='أيقونة الحساب'
    )
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'حساب'
        verbose_name_plural = 'الحسابات'
        ordering = ['name']
        unique_together = ['owner', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"
    
    def get_formatted_balance(self):
        """Get formatted balance with currency symbol"""
        return f"{self.current_balance:,.2f} {self.currency.symbol}"
    
    def update_balance(self, amount, transaction_type='income'):
        """Update account balance"""
        if transaction_type == 'income':
            self.current_balance += Decimal(str(amount))
        else:  # expense
            self.current_balance -= Decimal(str(amount))
        self.save()


class AccountTransfer(models.Model):
    """Model for transfers between accounts"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المستخدم')
    from_account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE,
        related_name='transfers_out',
        verbose_name='من حساب'
    )
    to_account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE,
        related_name='transfers_in',
        verbose_name='إلى حساب'
    )
    amount = models.DecimalField(
        max_digits=18, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='المبلغ'
    )
    exchange_rate = models.DecimalField(
        max_digits=18, 
        decimal_places=8, 
        default=1.0,
        verbose_name='سعر الصرف'
    )
    converted_amount = models.DecimalField(
        max_digits=18, 
        decimal_places=2,
        verbose_name='المبلغ المحول'
    )
    description = models.TextField(blank=True, null=True, verbose_name='وصف')
    transfer_date = models.DateTimeField(default=timezone.now, verbose_name='تاريخ التحويل')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'تحويل بين الحسابات'
        verbose_name_plural = 'التحويلات بين الحسابات'
        ordering = ['-transfer_date']
    
    def __str__(self):
        return f"تحويل من {self.from_account.name} إلى {self.to_account.name}"
    
    def save(self, *args, **kwargs):
        """Calculate converted amount and update balances"""
        self.converted_amount = self.amount * self.exchange_rate
        
        # Update balances
        self.from_account.current_balance -= self.amount
        self.from_account.save()
        
        self.to_account.current_balance += self.converted_amount
        self.to_account.save()
        
        super().save(*args, **kwargs)


class AccountTemplate(models.Model):
    """Templates for quick account creation"""
    name = models.CharField(max_length=200, verbose_name='اسم القالب')
    account_type = models.CharField(
        max_length=20, 
        choices=AccountType.choices,
        verbose_name='نوع الحساب'
    )
    default_currency = models.ForeignKey(
        Currency, 
        on_delete=models.CASCADE,
        verbose_name='العملة الافتراضية'
    )
    description = models.TextField(blank=True, null=True, verbose_name='وصف')
    color = models.CharField(
        max_length=7, 
        default='#007bff',
        verbose_name='لون الحساب'
    )
    icon = models.CharField(
        max_length=100, 
        default='fas fa-wallet',
        verbose_name='أيقونة الحساب'
    )
    is_public = models.BooleanField(default=True, verbose_name='عمومي')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='أنشأ بواسطة'
    )
    
    class Meta:
        verbose_name = 'قالب حساب'
        verbose_name_plural = 'قوالب الحسابات'
        ordering = ['name']
    
    def __str__(self):
        return self.name