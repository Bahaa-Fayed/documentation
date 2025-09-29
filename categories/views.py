"""
Views for categories app
"""
from django.shortcuts import render
from django.views.generic import ListView
from .models import Category


class CategoryListView(ListView):
    """List view for categories"""
    model = Category
    template_name = 'categories/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user).order_by('name')