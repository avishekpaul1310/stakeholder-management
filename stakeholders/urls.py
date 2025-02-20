from django.urls import path
from . import views

urlpatterns = [
    path('', views.StakeholderListView.as_view(), name='stakeholder-list'),
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('add/', views.StakeholderCreateView.as_view(), name='stakeholder-create'),
    path('<int:pk>/edit/', views.StakeholderUpdateView.as_view(), name='stakeholder-update'),
    path('<int:pk>/delete/', views.StakeholderDeleteView.as_view(), name='stakeholder-delete'),
    path('map/', views.StakeholderMapView.as_view(), name='stakeholder-map'),
    path('engagement-chart/', views.StakeholderEngagementChartView.as_view(), name='stakeholder-engagement-chart'),
]