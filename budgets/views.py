"""
Views for budgets app
"""
from django.shortcuts import render
from django.views.generic import ListView
from .models import Budget


class BudgetListView(ListView):
    """List view for budgets"""
    model = Budget
    template_name = 'budgets/budget_list.html'
    context_object_name = 'budgets'
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user).order_by('-created_at')