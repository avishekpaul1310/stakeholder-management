from django.urls import path
from . import views

urlpatterns = [
    path('', views.StakeholderListView.as_view(), name='stakeholder-list'),
    path('create/', views.StakeholderCreateView.as_view(), name='stakeholder-create'),
    path('update/<int:pk>/', views.StakeholderUpdateView.as_view(), name='stakeholder-update'),
    path('delete/<int:pk>/', views.StakeholderDeleteView.as_view(), name='stakeholder-delete'),
]