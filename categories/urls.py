"""
URL configuration for categories app
"""
from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
    # Category views
    path('', views.CategoryListView.as_view(), name='category_list'),
    # path('create/', views.CategoryCreateView.as_view(), name='category_create'),
    # path('<int:pk>/detail/', views.CategoryDetailView.as_view(), name='category_detail'),
    # path('<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_edit'),
    # path('<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
]