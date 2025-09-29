"""
URL configuration for expense_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.shortcuts import render


def home_view(request):
    """Home page view"""
    return render(request, 'home.html')


def health_check(request):
    """Health check endpoint"""
    return HttpResponse("OK", status=200)


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Home page
    path('', home_view, name='home'),
    
    # Health check endpoint
    path('health/', health_check, name='health_check'),
    
    # API URLs
    path('api/', include('api.urls', namespace='api')),
    
    # App URLs
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('categories/', include('categories.urls', namespace='categories')),
    path('transactions/', include('transactions.urls', namespace='transactions')),
    path('budgets/', include('budgets.urls', namespace='budgets')),
    path('reports/', include('reports.urls', namespace='reports')),
    path('goals/', include('goals.urls', namespace='goals')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)