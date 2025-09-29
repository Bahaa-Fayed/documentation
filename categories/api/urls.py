"""
URL configuration for categories API
"""
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, CategoryTemplateViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'templates', CategoryTemplateViewSet)

urlpatterns = router.urls