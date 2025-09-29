"""
URL configuration for budgets app
"""
from django.urls import path
from . import views

app_name = 'budgets'

urlpatterns = [
    # Budget views
    path('', views.BudgetListView.as_view(), name='budget_list'),
    # path('create/', views.BudgetCreateView.as_view(), name='budget_create'),
    # path('<int:pk>/detail/', views.BudgetDetailView.as_view(), name='budget_detail'),
]