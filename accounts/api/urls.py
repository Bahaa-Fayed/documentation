"""
URL configuration for accounts API
"""
from rest_framework.routers import DefaultRouter
from .views import CurrencyViewSet, AccountViewSet, AccountTransferViewSet, AccountTemplateViewSet

router = DefaultRouter()
router.register(r'currencies', CurrencyViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'transfers', AccountTransferViewSet)
router.register(r'templates', AccountTemplateViewSet)

urlpatterns = router.urls