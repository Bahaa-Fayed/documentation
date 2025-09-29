"""
URL configuration for API endpoints
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Initialize router
router = DefaultRouter()

# API URL patterns
urlpatterns = [
    # DRF
    path('auth/', include('rest_framework.urls')),
    
    # API router
    path('', include(router.urls)),
]

# Add routers later for each app
urlpatterns += [
    path('accounts/', include('accounts.api.urls')),
    path('categories/', include('categories.api.urls')),
    path('transactions/', include('transactions.api.urls')),
    path('budgets/', include('budgets.api.urls')),
    path('reports/', include('reports.api.urls')),
    path('goals/', include('goals.api.urls')),
]