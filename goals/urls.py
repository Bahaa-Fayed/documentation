"""
URL configuration for goals app
"""
from django.urls import path
from . import views

app_name = 'goals'

urlpatterns = [
    # Goal views
    path('', views.GoalListView.as_view(), name='goal_list'),
    # path('create/', views.GoalCreateView.as_view(), name='goal_create'),
    # path('<int:pk>/detail/', views.GoalDetailView.as_view(), name='goal_detail'),
]