# stakeholders/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Case, When, IntegerField, Value
from .models import Stakeholder, Engagement
from .forms import StakeholderForm, EngagementForm
from django.http import JsonResponse, HttpResponse
import json
import csv
import io

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

@login_required
def export_stakeholders(request):
    """Export stakeholders to a CSV file."""
    # Create the HttpResponse object with the appropriate CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="stakeholders.csv"'
    
    # Get stakeholders for the current user
    stakeholders = Stakeholder.objects.filter(created_by=request.user)
    
    # Create the CSV writer
    writer = csv.writer(response)
    writer.writerow(['name', 'role', 'organization', 'email', 'phone', 
                    'influence_level', 'interest_level', 'engagement_strategy', 
                    'desired_engagement', 'notes'])
    
    # Add stakeholder data
    for stakeholder in stakeholders:
        writer.writerow([
            stakeholder.name,
            stakeholder.role,
            stakeholder.organization,
            stakeholder.email,
            stakeholder.phone,
            stakeholder.influence_level,
            stakeholder.interest_level,
            stakeholder.engagement_strategy,
            stakeholder.desired_engagement,
            stakeholder.notes
        ])
    
    return response

@login_required
def export_template(request):
    """Export a CSV template for stakeholder import."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="stakeholder_template.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['name', 'role', 'organization', 'email', 'phone', 
                    'influence_level', 'interest_level', 'engagement_strategy', 
                    'desired_engagement', 'notes'])
    
    # Add a sample row to help users
    writer.writerow([
        'John Doe', 
        'CEO', 
        'Sample Company', 
        'john@example.com', 
        '555-123-4567',
        'High',  # Must be one of: High, Medium, Low
        'Medium',  # Must be one of: High, Medium, Low
        'Collaborate',  # Must be one of: Inform, Consult, Involve, Collaborate, Empower
        'Empower',  # Must be one of: Inform, Consult, Involve, Collaborate, Empower
        'Sample notes about this stakeholder'
    ])
    
    return response

@login_required
def import_stakeholders(request):
    """Import stakeholders from a CSV file."""
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        # Check if it's a CSV file
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('stakeholder_list')
        
        # Check file size (max 5MB)
        if csv_file.size > 5 * 1024 * 1024:
            messages.error(request, 'File is too large. Maximum size is 5MB.')
            return redirect('stakeholder_list')
            
        # Process the file
        try:
            csv_data = csv_file.read().decode('utf-8')
            io_string = io.StringIO(csv_data)
            reader = csv.DictReader(io_string)
            
            # Validate headers
            required_headers = ['name', 'role', 'influence_level', 'interest_level', 
                               'engagement_strategy', 'desired_engagement']
            
            # Get the headers from the CSV
            headers = reader.fieldnames
            
            # Check if all required headers are present
            missing_headers = [h for h in required_headers if h not in headers]
            if missing_headers:
                messages.error(request, f'Missing required headers: {", ".join(missing_headers)}')
                return redirect('stakeholder_list')
            
            # Valid choices for fields
            influence_choices = ['High', 'Medium', 'Low']
            engagement_choices = ['Inform', 'Consult', 'Involve', 'Collaborate', 'Empower']
            
            # Process rows
            row_count = 0
            success_count = 0
            error_rows = []
            
            for row in reader:
                row_count += 1
                
                # Validate required fields
                if not row['name'] or not row['role']:
                    error_rows.append(f"Row {row_count}: Missing required field 'name' or 'role'")
                    continue
                    
                # Validate choice fields
                if row['influence_level'] not in influence_choices:
                    error_rows.append(f"Row {row_count}: Invalid influence_level '{row['influence_level']}'")
                    continue
                    
                if row['interest_level'] not in influence_choices:
                    error_rows.append(f"Row {row_count}: Invalid interest_level '{row['interest_level']}'")
                    continue
                    
                if row['engagement_strategy'] not in engagement_choices:
                    error_rows.append(f"Row {row_count}: Invalid engagement_strategy '{row['engagement_strategy']}'")
                    continue
                    
                if row['desired_engagement'] not in engagement_choices:
                    error_rows.append(f"Row {row_count}: Invalid desired_engagement '{row['desired_engagement']}'")
                    continue
                
                # Create the stakeholder
                try:
                    stakeholder = Stakeholder(
                        name=row['name'],
                        role=row['role'],
                        organization=row.get('organization', ''),
                        email=row.get('email', ''),
                        phone=row.get('phone', ''),
                        influence_level=row['influence_level'],
                        interest_level=row['interest_level'],
                        engagement_strategy=row['engagement_strategy'],
                        desired_engagement=row['desired_engagement'],
                        notes=row.get('notes', ''),
                        created_by=request.user
                    )
                    stakeholder.save()
                    success_count += 1
                except Exception as e:
                    error_rows.append(f"Row {row_count}: Error saving stakeholder - {str(e)}")
            
            # Show success message
            if success_count:
                messages.success(request, f'Successfully imported {success_count} stakeholders.')
            
            # Show errors if any
            if error_rows:
                for error in error_rows[:5]:  # Show only first 5 errors
                    messages.warning(request, error)
                
                if len(error_rows) > 5:
                    messages.warning(request, f'... and {len(error_rows) - 5} more errors.')
            
        except Exception as e:
            messages.error(request, f'Error processing CSV file: {str(e)}')
        
        return redirect('stakeholder_list')
    
    # If not POST or no file
    messages.error(request, 'No file uploaded.')
    return redirect('stakeholder_list')