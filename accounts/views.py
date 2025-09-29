"""
Views for accounts app
"""
from django.shortcuts import render
from django.views.generic import ListView
from .models import Account


class AccountListView(ListView):
    """List view for accounts"""
    model = Account
    template_name = 'accounts/account_list.html'
    context_object_name = 'accounts'
    
    def get_queryset(self):
        return Account.objects.filter(owner=self.request.user).order_by('name')