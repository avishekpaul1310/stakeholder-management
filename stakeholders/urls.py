from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('stakeholders/', views.StakeholderListView.as_view(), name='stakeholder-list'),
    path('stakeholders/add/', views.StakeholderCreateView.as_view(), name='stakeholder-create'),
    path('stakeholders/<int:pk>/edit/', views.StakeholderUpdateView.as_view(), name='stakeholder-update'),
    path('stakeholders/<int:pk>/delete/', views.StakeholderDeleteView.as_view(), name='stakeholder-delete'),
    path('stakeholders/map/', views.StakeholderMapView.as_view(), name='stakeholder-map'),
    path('stakeholders/engagement-chart/', views.StakeholderEngagementChartView.as_view(), name='stakeholder-engagement-chart'),
]