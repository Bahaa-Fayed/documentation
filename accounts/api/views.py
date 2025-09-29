"""
Views for accounts API
"""
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Q
from ..models import Account, AccountTransfer, Currency, AccountTemplate
from .serializers import (
    AccountSerializer,
    AccountTransferSerializer,
    CurrencySerializer,
    AccountTemplateSerializer
)


class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Currency model"""
    queryset = Currency.objects.filter(is_active=True)
    serializer_class = CurrencySerializer
    permission_classes = [permissions.IsAuthenticated]


class AccountViewSet(viewsets.ModelViewSet):
    """ViewSet for Account model"""
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchBackend, filters.OrderingFilter]
    filterset_fields = ['account_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'current_balance']
    ordering = ['name']
    
    def get_queryset(self):
        """Return accounts owned by the current user"""
        return Account.objects.filter(owner=self.request.user).select_related('currency')
    
    def perform_create(self, serializer):
        """Set the owner when creating a new account"""
        serializer.save(owner=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get account summary statistics"""
        accounts = self.get_queryset()
        
        # Calculate totals by account type
        account_types = {}
        for account_type, _ in Account.AccountType.choices:
            total = accounts.filter(
                account_type=account_type, is_active=True
            ).aggregate(total=Sum('current_balance'))['total'] or 0
            account_types[account_type] = total
        
        # Overall statistics
        total_balance = accounts.filter(is_active=True).aggregate(
            total=Sum('current_balance')
        )['total'] or 0
        
        active_accounts = accounts.filter(is_active=True).count()
        total_accounts = accounts.count()
        
        return Response({
            'total_balance': total_balance,
            'active_accounts': active_accounts,
            'total_accounts': total_accounts,
            'account_types': account_types
        })


class AccountTransferViewSet(viewsets.ModelViewSet):
    """ViewSet for AccountTransfer model"""
    serializer_class = AccountTransferSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['from_account', 'to_account']
    ordering_fields = ['transfer_date', 'amount']
    ordering = ['-transfer_date']
    
    def get_queryset(self):
        """Return transfers for user's accounts"""
        user_accounts = Account.objects.filter(owner=self.request.user).values_list('id', flat=True)
        return AccountTransfer.objects.filter(
            Q(from_account__in=user_accounts) | Q(to_account__in=user_accounts)
        ).select_related('from_account', 'to_account')
    
    def perform_create(self, serializer):
        """Set the user when creating a new transfer"""
        serializer.save(user=self.request.user)


class AccountTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AccountTemplate model"""
    queryset = AccountTemplate.objects.filter(is_public=True)
    serializer_class = AccountTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchBackend]
    filterset_fields = ['account_type', 'is_public']
    search_fields = ['name', 'description']
    ordering = ['name']