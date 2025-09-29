"""
Admin configuration for goals app
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import FinancialGoal, GoalContribution, GoalMilestone, GoalTemplate


class GoalMilestoneInline(admin.TabularInline):
    model = GoalMilestone
    extra = 0
    fields = ['name', 'target_amount', 'target_date', 'is_achieved', 'achieved_date']
    readonly_fields = ['achieved_date']


class GoalContributionInline(admin.TabularInline):
    model = GoalContribution
    extra = 0
    fields = ['amount', 'contribution_type', 'account', 'contribution_date']
    readonly_fields = ['contribution_date']


@admin.register(FinancialGoal)
class FinancialGoalAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'goal_type', 'priority', 'target_amount_display',
        'current_amount_display', 'progress_bar', 'target_date', 'status', 'user'
    ]
    list_filter = ['goal_type', 'priority', 'status', 'user']
    search_fields = ['name', 'description', 'user__username']
    ordering = ['priority', 'target_date']
    readonly_fields = [
        'current_amount', 'created_at', 'updated_at', 'completed_date'
    ]
    
    inlines = [GoalMilestoneInline, GoalContributionInline]
    
    fieldsets = (
        ('معلومات الهدف', {
            'fields': ('user', 'name', 'description', 'goal_type', 'priority')
        }),
        ('المبالغ المالية', {
            'fields': ('target_amount', 'current_amount', 'monthly_target')
        }),
        ('الجدول الزمني', {
            'fields': ('start_date', 'target_date', 'completed_date')
        }),
        ('الحساب والتصنيف', {
            'fields': ('account', 'category')
        }),
        ('التنسيق', {
            'fields': ('color', 'icon')
        }),
        ('الحالة', {
            'fields': ('status',)
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def target_amount_display(self, obj):
        return f"{obj.target_amount:,.2f}"
    target_amount_display.short_description = "المبلغ المستهدف"
    
    def current_amount_display(self, obj):
        return f"{obj.current_amount:,.2f}"
    current_amount_display.short_description = "المبلغ الحالي"
    
    def progress_bar(self, obj):
        percentage = obj.get_progress_percentage()
        remaining_percentage = max(100 - percentage, 0)
        
        color = obj.get_progress_status()['color']
        
        progress_html = '''
            <div style="width: 100px; height: 20px; border: 1px solid #ccc; background-color: #f0f0f0; position: relative;">
                <div style="width: {}%; height: 100%; background-color: {}; position: absolute; top: 0; left: 0;"></div>
                <div style="width: {}%; height: 100%; background-color: #e9ecef; position: absolute; top: 0; right: 0;"></div>
            </div>
        '''.format(percentage, color, remaining_percentage)
        
        return format_html('<div>{}</div><small>{:.1f}%</small>', progress_html, percentage)
    progress_bar.short_description = "التقدم"


@admin.register(GoalContribution)
class GoalContributionAdmin(admin.ModelAdmin):
    list_display = [
        'goal_display', 'amount', 'contribution_type', 'account',
        'contribution_date', 'transaction_link'
    ]
    list_filter = ['contribution_type', 'contribution_date']
    search_fields = ['goal__name', 'account__name', 'description']
    ordering = ['-contribution_date']
    readonly_fields = ['contribution_date', 'created_at']
  
    def goal_display(self, obj):
        return obj.goal.name
    goal_display.short_description = "الهدف"
    
    def transaction_link(self, obj):
        if obj.transaction:
            return format_html(
                '<a href="/admin/transactions/transaction/{}/change/">{}</a>',
                obj.transaction.id,
                str(obj.transaction.id)[:8]
            )
        return '-'
    transaction_link.short_description = "المعاملة المرتبطة"


@admin.register(GoalMilestone)
class GoalMilestoneAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'goal_display', 'target_amount_display', 'target_date', 'is_achieved', 'achieved_date'
    ]
    list_filter = ['is_achieved', 'target_date']
    search_fields = ['name', 'goal__name', 'description']
    ordering = ['target_amount']
    readonly_fields = ['achieved_date', 'created_at']
    
    def goal_display(self, obj):
        return obj.goal.name
    goal_display.short_description = "الهدف"
    
    def target_amount_display(self, obj):
        return f"{obj.target_amount:,.2f}"
    target_amount_display.short_description = "المبلغ المستهدف"


@admin.register(GoalTemplate)
class GoalTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'goal_type', 'priority', 'default_duration_months',
        'usage_count', 'is_public', 'created_by'
    ]
    list_filter = ['goal_type', 'priority', 'is_public']
    search_fields = ['name', 'description']
    ordering = ['-usage_count', 'name']
    readonly_fields = ['usage_count', 'created_at']
    
    fieldsets = (
        ('معلومات القالب', {
            'fields': ('name', 'description', 'created_by')
        }),
        ('إعدادات الهدف', {
            'fields': ('goal_type', 'priority', 'default_duration_months')
        }),
        ('التنسيق', {
            'fields': ('color', 'icon')
        }),
        ('الإعدادات العامة', {
            'fields': ('is_public',)
        }),
        ('الإحصائيات', {
            'fields': ('usage_count', 'created_at')
        }),
    )