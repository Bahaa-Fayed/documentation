"""
Serializers for categories API
"""
from rest_framework import serializers
from ..models import Category, CategoryTemplate


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    children_count = serializers.SerializerMethodField()
    monthly_spending = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'parent', 'parent_name', 'category_type',
            'color', 'icon', 'description', 'is_active', 'sort_order',
            'budget_limit', 'children_count', 'monthly_spending',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_children_count(self, obj):
        """Get number of children categories"""
        return obj.get_children_count()
    
    def get_monthly_spending(self, obj):
        """Get current month spending"""
        from datetime import datetime
        current_date = datetime.now()
        return obj.get_monthly_spending(current_date.year, current_date.month)


class CategoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating categories"""
    
    class Meta:
        model = Category
        fields = [
            'name', 'parent', 'category_type', 'color', 'icon',
            'description', 'sort_order', 'budget_limit'
        ]


class CategoryTemplateSerializer(serializers.ModelSerializer):
    """Serializer for CategoryTemplate model"""
    
    class Meta:
        model = CategoryTemplate
        fields = [
            'id', 'name', 'parent_name', 'category_type', 'color',
            'icon', 'description', 'budget_limit', 'is_public',
            'sort_order', 'usage_count'
        ]
        read_only_fields = ['id', 'usage_count']


class CategoryHierarchySerializer(serializers.ModelSerializer):
    """Serializer for category hierarchy (flattened structure)"""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'category_type', 'color', 'icon', 'parent']
        depth = 1