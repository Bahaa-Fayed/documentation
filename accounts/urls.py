"""
URL configuration for accounts app
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Account views
    path('', views.AccountListView.as_view(), name='account_list'),
    # path('create/', views.AccountCreateView.as_view(), name='account_create'),
    # path('<int:pk>/detail/', views.AccountDetailView.as_view(), name='account_detail'),
    # path('<int:pk>/update/', views.AccountUpdateView.as_view(), name='account_edit'),
    # path('<int:pk>/delete/', views.AccountDeleteView.as_view(), name='account_delete'),
    
    # Transfer views
    # path('transfer/', views.TransferCreateView.as_view(), name='transfer_create'),
    # path('transfer/<int:pk>/', views.TransferDetailView.as_view(), name='transfer_detail'),
]