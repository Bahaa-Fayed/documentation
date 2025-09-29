"""
Views for goals app
"""
from django.shortcuts import render
from django.views.generic import ListView
from .models import FinancialGoal


class GoalListView(ListView):
    """List view for goals"""
    model = FinancialGoal
    template_name = 'goals/goal_list.html'
    context_object_name = 'goals'
    
    def get_queryset(self):
        return FinancialGoal.objects.filter(user=self.request.user).order_by('-created_at')