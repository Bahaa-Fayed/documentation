"""
Views for categories API
"""
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from ..models import Category, CategoryTemplate
from .serializers import (
    CategorySerializer,
    CategoryCreateSerializer,
    CategoryTemplateSerializer,
    CategoryHierarchySerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category model"""
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchBackend, filters.OrderingFilter]
    filterset_fields = ['category_type', 'is_active', 'parent']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'sort_order', 'created_at']
    ordering = ['sort_order', 'name']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return CategoryCreateSerializer
        elif self.action == 'hierarchy':
            return CategoryHierarchySerializer
        return CategorySerializer
    
    def get_queryset(self):
        """Return categories belonging to the current user"""
        return Category.objects.filter(user=self.request.user).select_related('parent')
    
    def perform_create(self, serializer):
        """Set the user when creating a new category"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def hierarchy(self, request):
        """Get category hierarchy"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        
        # Build hierarchy structure
        categories_dict = {}
        top_level_categories = []
        
        for category in serializer.data:
            categories_dict[category['id']] = category
            category['children'] = []
            
            if category['parent'] is None:
                top_level_categories.append(category)
        
        # Assign children to parents
        for category in serializer.data:
            if category['parent'] is not None:
                parent_id = category['parent']
                if parent_id in categories_dict:
                    categories_dict[parent_id]['children'].append(category)
        
        return Response(top_level_categories)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get category statistics"""
        queryset = self.get_queryset()
        
        stats = queryset.filter(is_active=True).aggregate(
            total_categories=Count('id'),
            income_categories=Count('id', filter=models.Q(category_type='income')),
            expense_categories=Count('id', filter=models.Q(category_type='expense')),
            transfer_categories=Count('id', filter=models.Q(category_type='transfer')),
            categories_with_budget=Count('id', filter=models.Q(budget_limit__isnull=False))
        )
        
        return Response(stats)


class CategoryTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for CategoryTemplate model"""
    queryset = CategoryTemplate.objects.filter(is_public=True)
    serializer_class = CategoryTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchBackend, filters.OrderingFilter]
    filterset_fields = ['category_type', 'is_public']
    search_fields = ['name', 'parent_name', 'description']
    ordering_fields = ['name', 'usage_count']
    ordering = ['-usage_count', 'name']
    
    @action(detail=True, methods=['post'])
    def apply_template(self, request, pk=None):
        """Apply template to create a category for the user"""
        template = self.get_object()
        user = request.user
        
        # Create category from template
        category_data = {
            'user': user,
            'name': template.name,
            'parent': None,  # Will be set if parent exists
            'category_type': template.category_type,
            'color': template.color,
            'icon': template.icon,
            'description': template.description or '',
            'budget_limit': template.budget_limit,
            'sort_order': template.sort_order
        }
        
        # Find parent category if it exists
        if template.parent_name:
            parent_category = Category.objects.filter(
                user=user,
                name=template.parent_name,
                category_type=template.category_type
            ).first()
            if parent_category:
                category_data['parent'] = parent_category
        
        # Update usage count
        CategoryTemplate.objects.filter(pk=pk).update(
            usage_count=models.F('usage_count') + 1
        )
        
        category = Category.objects.create(**category_data)
        serializer = CategorySerializer(category)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Import models for referencing in aggregations
from django.db import models