# stakeholders/views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Stakeholder
from .forms import StakeholderForm
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q, Avg, Count, F
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models.functions import Abs
from .mixins import AdminRequiredMixin, ViewerPermissionMixin

class StakeholderListView(ViewerPermissionMixin, ListView):
    model = Stakeholder
    template_name = 'stakeholders/stakeholder_list.html'
    context_object_name = 'stakeholders'
    ordering = ['name']  # Default ordering

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        role_filter = self.request.GET.get('role', '')
        org_filter = self.request.GET.get('organization', '')
        sort_by = self.request.GET.get('sort', 'name')

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(role__icontains=search_query) |
                Q(organization__icontains=search_query)
            )
        if role_filter:
            queryset = queryset.filter(role__iexact=role_filter)
        if org_filter:
            queryset = queryset.filter(organization__iexact=org_filter)
        
        return queryset.order_by(sort_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = Stakeholder.objects.values_list('role', flat=True).distinct()
        context['organizations'] = Stakeholder.objects.values_list('organization', flat=True).distinct()
        context['current_sort'] = self.request.GET.get('sort', 'name')
        return context

class StakeholderCreateView(AdminRequiredMixin, CreateView):
    model = Stakeholder
    form_class = StakeholderForm
    template_name = 'stakeholders/stakeholder_form.html'
    success_url = reverse_lazy('stakeholder-list')

    def form_valid(self, form):
        messages.success(self.request, 'Stakeholder created successfully!')
        return super().form_valid(form)

class StakeholderUpdateView(AdminRequiredMixin, UpdateView):
    model = Stakeholder
    form_class = StakeholderForm
    template_name = 'stakeholders/stakeholder_form.html'
    success_url = reverse_lazy('stakeholder-list')

    def form_valid(self, form):
        messages.success(self.request, 'Stakeholder updated successfully!')
        return super().form_valid(form)

class StakeholderDeleteView(AdminRequiredMixin, DeleteView):
    model = Stakeholder
    template_name = 'stakeholders/stakeholder_confirm_delete.html'
    success_url = reverse_lazy('stakeholder-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Stakeholder deleted successfully!')
        return super().delete(request, *args, **kwargs)
    
class StakeholderMapView(ViewerPermissionMixin, TemplateView):
    template_name = 'stakeholders/stakeholder_map.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stakeholders = Stakeholder.objects.all()
        context['stakeholders'] = stakeholders
        # Add this line to create JSON data for the chart
        context['stakeholders_json'] = json.dumps(
            [{'name': s.name, 'power': s.power, 'interest': s.interest} 
             for s in stakeholders],
            cls=DjangoJSONEncoder
        )
        return context

class StakeholderEngagementChartView(ViewerPermissionMixin, TemplateView):
    template_name = 'stakeholders/stakeholder_engagement_chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stakeholders = Stakeholder.objects.all()
        context['stakeholders'] = stakeholders
        context['stakeholders_json'] = json.dumps(
            [{'name': s.name, 
              'current': s.current_engagement_level, 
              'desired': s.desired_engagement_level} 
             for s in stakeholders],
            cls=DjangoJSONEncoder
        )
        return context
    
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'stakeholders/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Total Stakeholders
        context['total_stakeholders'] = Stakeholder.objects.count()
        
        # Key Players (Power >= 5 and Interest >= 5)
        context['key_players'] = Stakeholder.objects.filter(
            power__gte=5,
            interest__gte=5
        ).count()
        
        # Average Engagement Gap
        context['avg_engagement_gap'] = Stakeholder.objects.annotate(
            engagement_gap=Abs(F('desired_engagement_level') - F('current_engagement_level'))
        ).aggregate(Avg('engagement_gap'))['engagement_gap__avg'] or 0
        
        # Stakeholders with significant gaps (gap > 1)
        context['attention_needed'] = Stakeholder.objects.annotate(
            gap=F('desired_engagement_level') - F('current_engagement_level')
        ).filter(gap__gt=1).count()
        
        # Recent stakeholders
        context['recent_stakeholders'] = Stakeholder.objects.order_by('-created_at')[:5]
        
        return context