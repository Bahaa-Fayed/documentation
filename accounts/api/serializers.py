"""
Serializers for accounts API
"""
from rest_framework import serializers
from ..models import Currency, Account, AccountTransfer, AccountTemplate


class CurrencySerializer(serializers.ModelSerializer):
    """Serializer for Currency model"""
    
    class Meta:
        model = Currency
        fields = ['id', 'code', 'name', 'symbol', 'exchange_rate', 'is_primary', 'is_active']
        read_only_fields = ['id']


class AccountSerializer(serializers.ModelSerializer):
    """Serializer for Account model"""
    currency_details = CurrencySerializer(source='currency', read_only=True)
    
    class Meta:
        model = Account
        fields = [
            'id', 'name', 'account_type', 'currency', 'currency_details',
            'initial_balance', 'current_balance', 'description', 'color',
            'icon', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'current_balance', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        """Validate account name uniqueness per user"""
        user = self.context['request'].user
        if self.instance:
            # For updates, exclude current instance
            if Account.objects.filter(owner=user, name=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Account with this name already exists.")
        else:
            # For creation
            if Account.objects.filter(owner=user, name=value).exists():
                raise serializers.ValidationError("Account with this name already exists.")
        return value


class AccountTransferSerializer(serializers.ModelSerializer):
    """Serializer for AccountTransfer model"""
    from_account_name = serializers.CharField(source='from_account.name', read_only=True)
    to_account_name = serializers.CharField(source='to_account.name', read_only=True)
    
    class Meta:
        model = AccountTransfer
        fields = [
            'id', 'from_account', 'to_account', 'from_account_name', 'to_account_name',
            'amount', 'exchange_rate', 'converted_amount', 'description',
            'transfer_date', 'created_at'
        ]
        read_only_fields = ['id', 'converted_amount', 'created_at']


class AccountTemplateSerializer(serializers.ModelSerializer):
    """Serializer for AccountTemplate model"""
    
    class Meta:
        model = AccountTemplate
        fields = [
            'id', 'name', 'account_type', 'default_currency',
            'description', 'color', 'icon', 'is_public', 'created_by'
        ]
        read_only_fields = ['id', 'created_by']