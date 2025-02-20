# stakeholders/views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Stakeholder
from .forms import StakeholderForm
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q

class StakeholderListView(ListView):
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

class StakeholderCreateView(CreateView):
    model = Stakeholder
    form_class = StakeholderForm
    template_name = 'stakeholders/stakeholder_form.html'
    success_url = reverse_lazy('stakeholder-list')

    def form_valid(self, form):
        messages.success(self.request, 'Stakeholder created successfully!')
        return super().form_valid(form)

class StakeholderUpdateView(UpdateView):
    model = Stakeholder
    form_class = StakeholderForm
    template_name = 'stakeholders/stakeholder_form.html'
    success_url = reverse_lazy('stakeholder-list')

    def form_valid(self, form):
        messages.success(self.request, 'Stakeholder updated successfully!')
        return super().form_valid(form)

class StakeholderDeleteView(DeleteView):
    model = Stakeholder
    template_name = 'stakeholders/stakeholder_confirm_delete.html'
    success_url = reverse_lazy('stakeholder-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Stakeholder deleted successfully!')
        return super().delete(request, *args, **kwargs)
    
class StakeholderMapView(TemplateView):
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

class StakeholderEngagementChartView(TemplateView):
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