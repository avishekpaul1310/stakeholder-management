from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('list/', views.stakeholder_list, name='stakeholder_list'),
    path('create/', views.stakeholder_create, name='stakeholder_create'),
    path('<int:pk>/update/', views.stakeholder_update, name='stakeholder_update'),
    path('<int:pk>/delete/', views.stakeholder_delete, name='stakeholder_delete'),
    path('<int:pk>/detail/', views.stakeholder_detail, name='stakeholder_detail'),
    path('engagement/create/', views.engagement_create, name='engagement_create'),
    path('<int:stakeholder_id>/engagement/create/', views.engagement_create, name='stakeholder_engagement_create'),
    path('mapping/', views.stakeholder_mapping, name='stakeholder_mapping'),
    path('api/grid-data/', views.stakeholder_grid_data, name='stakeholder_grid_data'),
    path('analysis/', views.stakeholder_analysis, name='stakeholder_analysis'),
    path('api/stakeholder-data/', views.get_stakeholder_data, name='get_stakeholder_data'),
]