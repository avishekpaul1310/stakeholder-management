# stakeholders/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Case, When, IntegerField, Value
from .models import Stakeholder, Engagement
from .forms import StakeholderForm, EngagementForm
from django.http import JsonResponse
import json

@login_required
def dashboard(request):
    stakeholders = Stakeholder.objects.filter(created_by=request.user)
    engagement_stats = Stakeholder.objects.filter(created_by=request.user).values(
        'engagement_strategy').annotate(count=Count('engagement_strategy'))
    influence_stats = Stakeholder.objects.filter(created_by=request.user).values(
        'influence_level').annotate(count=Count('influence_level'))
    
    context = {
        'stakeholders': stakeholders,
        'engagement_stats': engagement_stats,
        'influence_stats': influence_stats,
        'total_stakeholders': stakeholders.count()
    }
    return render(request, 'stakeholders/dashboard.html', context)

@login_required
def stakeholder_list(request):
    stakeholders = Stakeholder.objects.filter(created_by=request.user)
    return render(request, 'stakeholders/stakeholder_list.html', {'stakeholders': stakeholders})

@login_required
def stakeholder_create(request):
    if request.method == 'POST':
        form = StakeholderForm(request.POST)
        if form.is_valid():
            stakeholder = form.save(commit=False)
            stakeholder.created_by = request.user
            stakeholder.save()
            messages.success(request, 'Stakeholder created successfully!')
            return redirect('stakeholder_list')
    else:
        form = StakeholderForm()
    return render(request, 'stakeholders/stakeholder_form.html', {'form': form, 'action': 'Create'})

@login_required
def stakeholder_update(request, pk):
    stakeholder = get_object_or_404(Stakeholder, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = StakeholderForm(request.POST, instance=stakeholder)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stakeholder updated successfully!')
            return redirect('stakeholder_list')
    else:
        form = StakeholderForm(instance=stakeholder)
    return render(request, 'stakeholders/stakeholder_form.html', {'form': form, 'stakeholder': stakeholder, 'action': 'Update'})

@login_required
def stakeholder_delete(request, pk):
    stakeholder = get_object_or_404(Stakeholder, pk=pk, created_by=request.user)
    if request.method == 'POST':
        stakeholder.delete()
        messages.success(request, 'Stakeholder deleted successfully!')
        return redirect('stakeholder_list')
    return render(request, 'stakeholders/stakeholder_confirm_delete.html', {'stakeholder': stakeholder})

@login_required
def stakeholder_detail(request, pk):
    stakeholder = get_object_or_404(Stakeholder, pk=pk, created_by=request.user)
    engagements = stakeholder.engagements.all()
    return render(request, 'stakeholders/stakeholder_detail.html', {'stakeholder': stakeholder, 'engagements': engagements})

@login_required
def engagement_create(request, stakeholder_id=None):
    stakeholder = None
    if stakeholder_id:
        stakeholder = get_object_or_404(Stakeholder, pk=stakeholder_id, created_by=request.user)
    
    if request.method == 'POST':
        form = EngagementForm(request.POST)
        if form.is_valid():
            engagement = form.save(commit=False)
            engagement.created_by = request.user
            engagement.save()
            messages.success(request, 'Engagement recorded successfully!')
            return redirect('stakeholder_detail', pk=engagement.stakeholder.pk)
    else:
        initial = {}
        if stakeholder:
            initial = {'stakeholder': stakeholder}
        form = EngagementForm(initial=initial)
        
    # If this is for a specific stakeholder, limit the stakeholder choices
    if stakeholder:
        form.fields['stakeholder'].queryset = Stakeholder.objects.filter(pk=stakeholder.pk)
    else:
        form.fields['stakeholder'].queryset = Stakeholder.objects.filter(created_by=request.user)
    
    return render(request, 'stakeholders/engagement_form.html', {'form': form})

@login_required
def stakeholder_mapping(request):
    """View for the stakeholder power/interest grid."""
    stakeholders = Stakeholder.objects.filter(created_by=request.user)
    return render(request, 'stakeholders/stakeholder_mapping.html', {'stakeholders': stakeholders})

@login_required
def stakeholder_analysis(request):
    """View for the stakeholder engagement assessment."""
    stakeholders = Stakeholder.objects.filter(created_by=request.user)
    return render(request, 'stakeholders/stakeholder_analysis.html', {'stakeholders': stakeholders})

@login_required
def get_stakeholder_data(request):
    """API endpoint to fetch stakeholder data for charts and grids."""
    stakeholders = Stakeholder.objects.filter(created_by=request.user)
    
    stakeholder_data = []
    for stakeholder in stakeholders:
        stakeholder_data.append({
            'id': stakeholder.id,
            'name': stakeholder.name,
            'role': stakeholder.role,
            'organization': stakeholder.organization,
            'influence': stakeholder.get_influence_value(),
            'interest': stakeholder.get_interest_value(),
            'current_engagement': stakeholder.get_engagement_level_value(),
            'desired_engagement': stakeholder.get_desired_engagement_level_value(),
            'quadrant': stakeholder.get_quadrant()
        })
    
    return JsonResponse({'stakeholders': stakeholder_data})

@login_required
def stakeholder_grid_data(request):
    """API endpoint to fetch stakeholder data specifically for the grid visualization."""
    stakeholders = Stakeholder.objects.filter(created_by=request.user)
    
    grid_data = []
    for stakeholder in stakeholders:
        grid_data.append({
            'id': stakeholder.id,
            'name': stakeholder.name,
            'role': stakeholder.role,
            'organization': stakeholder.organization,
            'influence_level': stakeholder.influence_level,
            'interest_level': stakeholder.interest_level,
            'influence_value': stakeholder.get_influence_value(),
            'interest_value': stakeholder.get_interest_value(),
            'quadrant': stakeholder.get_quadrant()
        })
    
    return JsonResponse({'stakeholders': grid_data})