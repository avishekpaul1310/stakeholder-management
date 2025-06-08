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
    path('export/', views.export_stakeholders, name='export_stakeholders'),
    path('export/template/', views.export_template, name='export_template'),
    path('import/', views.import_stakeholders, name='import_stakeholders'),
    
    # AI Insights
    path('<int:pk>/insights/', views.get_stakeholder_insights, name='stakeholder_insights'),
    path('insights/<int:pk>/helpful/', views.mark_insight_helpful, name='mark_insight_helpful'),
    path('report/generate/', views.generate_report, name='generate_report'),
    
    # Activity Feed
    path('activity/', views.activity_feed, name='activity_feed'),
    
    # Tags
    path('tags/', views.tag_list, name='tag_list'),
    path('tags/create/', views.create_tag, name='create_tag'),
    path('tags/<int:pk>/delete/', views.delete_tag, name='delete_tag'),
    path('<int:stakeholder_id>/add-tags/', views.add_tag_to_stakeholder, name='add_tags_to_stakeholder'),
    path('<int:stakeholder_id>/remove-tag/<int:tag_id>/', views.remove_tag_from_stakeholder, name='remove_tag_from_stakeholder'),
    
    # Relationships
    path('relationships/', views.relationship_list, name='relationship_list'),
    path('relationships/create/', views.create_relationship, name='create_relationship'),
    path('relationships/<int:pk>/delete/', views.delete_relationship, name='delete_relationship'),
    path('network/', views.stakeholder_network, name='stakeholder_network'),
]