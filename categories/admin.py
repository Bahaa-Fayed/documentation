"""
Admin configuration for categories app
"""

from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import redirect
from django.contrib import messages
from .models import Category, CategoryTemplate


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'category_type', 'parent', 'budget_limit', 'is_active', 'created_at']
    list_filter = ['category_type', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'user__username']
    ordering = ['user', 'sort_order', 'name']
    list_editable = ['is_active']
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('user', 'name', 'parent', 'category_type', 'description')
        }),
        ('التنسيق والترتيب', {
            'fields': ('color', 'icon', 'sort_order')
        }),
        ('الميزانية', {
            'fields': ('budget_limit',)
        }),
        ('الحالة', {
            'fields': ('is_active',)
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'parent')
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # If editing existing category, ensure categories belong to same user
        if obj:
            if obj.parent:
                parent_categories = Category.objects.filter(
                    user=obj.user,
                    pk__not=obj.pk
                ).values_list('pk', 'name')
            else:
                parent_categories = Category.objects.filter(user=obj.user).values_list('pk', 'name')
        else:
            # For new categories, filter parent choices by current user
            parent_categories = Category.objects.filter(user__pk=request.user.pk).values_list('pk', 'name')
        
        form.base_fields['parent'].choices = [(None, '---------')] + list(parent_categories)
        return form


@admin.register(CategoryTemplate)
class CategoryTemplateAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'category_type', 'usage_count', 'is_public']
    list_filter = ['category_type', 'is_public']
    search_fields = ['name', 'parent_name', 'description']
    ordering = ['-usage_count', 'name']
    readonly_fields = ['usage_count']
    
    def display_name(self, obj):
        return obj.__str__()
    display_name.short_description = "اسم التصنيف"


@admin.action(description="إعادة ترتيب التصنيفات")
def reorder_categories(modeladmin, request, queryset):
    """Reorder categories by user"""
    users = queryset.values_list('user', flat=True).distinct()
    for user_id in users:
        categories = Category.objects.filter(
            user_id=user_id,
            parent__isnull=True
        ).order_by('name')
        
        for index, category in enumerate(categories):
            category.sort_order = index + 1
            category.save()


CategoryAdmin.actions = [reorder_categories]