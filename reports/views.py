"""
Views for reports app
"""
from django.shortcuts import render
from django.views.generic import ListView
from .models import ReportExecution


class ReportListView(ListView):
    """List view for reports"""
    model = ReportExecution
    template_name = 'reports/report_list.html'
    context_object_name = 'reports'
    
    def get_queryset(self):
        return ReportExecution.objects.filter(user=self.request.user).order_by('-created_at')