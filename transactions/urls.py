"""
URL configuration for transactions app
"""
from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    # Transaction views
    path('', views.TransactionListView.as_view(), name='transaction_list'),
    # path('create/', views.TransactionCreateView.as_view(), name='transaction_create'),
    # path('<uuid:pk>/detail/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    # path('<uuid:pk>/update/', views.TransactionUpdateView.as_view(), name='transaction_edit'),
    # path('<uuid:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction_delete'),
    
    # Template views
    # path('templates/', views.TransactionTemplateListView.as_view(), name='template_list'),
    # path('templates/create/', views.TransactionTemplateCreateView.as_view(), name='template_create'),
]