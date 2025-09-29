"""
URL configuration for reports app
"""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Report views
    path('', views.ReportListView.as_view(), name='report_list'),
    # path('create/', views.ReportCreateView.as_view(), name='report_create'),
    # path('generate/', views.ReportGenerateView.as_view(), name='report_generate'),
]