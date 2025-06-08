# stakeholders/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Case, When, IntegerField, Value
from .models import Stakeholder, Engagement, StakeholderInsight, Activity, Tag, StakeholderRelationship, StakeholderReminder
from .forms import StakeholderForm, EngagementForm
from django.http import JsonResponse, HttpResponse
import json
import csv
import io
from .utils import generate_stakeholder_insights, generate_stakeholder_report
from django.utils import timezone

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
        form = StakeholderForm(request.POST, user=request.user)
        if form.is_valid():
            stakeholder = form.save(commit=False)
            stakeholder.created_by = request.user
            stakeholder.save()
            
            # Handle the many-to-many relationship for tags
            if form.cleaned_data.get('tags'):
                form.save_m2m()  # This saves the tags
            
            # Log activity
            Activity.objects.create(
                user=request.user,
                activity_type='created',
                stakeholder_name=stakeholder.name,
                stakeholder_id=stakeholder.id,
                description=f"Created stakeholder {stakeholder.name}"
            )
            
            messages.success(request, 'Stakeholder created successfully!')
            return redirect('stakeholder_detail', pk=stakeholder.id)
    else:
        form = StakeholderForm(user=request.user)
    return render(request, 'stakeholders/stakeholder_form.html', {'form': form, 'action': 'Create'})

@login_required
def stakeholder_update(request, pk):
    stakeholder = get_object_or_404(Stakeholder, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = StakeholderForm(request.POST, instance=stakeholder, user=request.user)
        if form.is_valid():
            stakeholder = form.save()
            
            # Log activity
            Activity.objects.create(
                user=request.user,
                activity_type='updated',
                stakeholder_name=stakeholder.name,
                stakeholder_id=stakeholder.id,
                description=f"Updated stakeholder {stakeholder.name}"
            )
            
            messages.success(request, 'Stakeholder updated successfully!')
            return redirect('stakeholder_detail', pk=stakeholder.id)
    else:
        form = StakeholderForm(instance=stakeholder, user=request.user)
    return render(request, 'stakeholders/stakeholder_form.html', {'form': form, 'stakeholder': stakeholder, 'action': 'Update'})

@login_required
def stakeholder_delete(request, pk):
    stakeholder = get_object_or_404(Stakeholder, pk=pk, created_by=request.user)
    if request.method == 'POST':
        # Log activity before deletion
        stakeholder_name = stakeholder.name
        
        # Save a copy of relationships for logging
        from_relationships = list(stakeholder.relationships_from.all())
        to_relationships = list(stakeholder.relationships_to.all())
        
        # Delete the stakeholder
        stakeholder.delete()
        
        # Log deletion activity
        Activity.objects.create(
            user=request.user,
            activity_type='deleted',
            stakeholder_name=stakeholder_name,
            description=f"Deleted stakeholder {stakeholder_name}"
        )
        
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
            
            # Log activity
            Activity.objects.create(
                user=request.user,
                activity_type='engagement',
                stakeholder_name=engagement.stakeholder.name,
                stakeholder_id=engagement.stakeholder.id,
                description=f"Recorded engagement with {engagement.stakeholder.name} on {engagement.date}"
            )
            
            messages.success(request, 'Engagement recorded successfully!')
            return redirect('stakeholder_detail', pk=engagement.stakeholder.pk)
    else:
        initial = {}
        if stakeholder:
            initial = {
                'stakeholder': stakeholder,
                'date': timezone.now().date(),
            }
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


@login_required
def get_stakeholder_insights(request, pk):
    """Generate insights for a stakeholder using Gemini AI"""
    stakeholder = get_object_or_404(Stakeholder, pk=pk, created_by=request.user)
    
    # Check if insights were generated in the last 24 hours
    recent_insight = StakeholderInsight.objects.filter(
        stakeholder=stakeholder, 
        created_at__gte=timezone.now() - timezone.timedelta(hours=24)
    ).first()
    
    if recent_insight:
        insight = recent_insight
        is_new = False
    else:
        # Generate new insights
        insight = generate_stakeholder_insights(stakeholder, request.user)
        is_new = True
    
    if isinstance(insight, str):  # Error case
        return JsonResponse({'error': insight}, status=400)
      # Return the insights
    return JsonResponse({
        'insight_text': insight.insight_text,
        'created_at': insight.created_at.strftime('%Y-%m-%d %H:%M'),
        'is_new': is_new,
        'insight_id': insight.id
    })


@login_required
def mark_insight_helpful(request, pk):
    """Mark an insight as helpful or not helpful"""
    insight = get_object_or_404(StakeholderInsight, pk=pk)
    
    # Check if the insight belongs to a stakeholder created by the user
    if insight.stakeholder.created_by != request.user:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    # Get the helpful status from the request
    data = json.loads(request.body)
    is_helpful = data.get('is_helpful')
    
    insight.is_helpful = is_helpful
    insight.save()
    
    return JsonResponse({'status': 'success'})


@login_required
def generate_report(request):
    """Generate a stakeholder management report using Gemini AI"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # API call for generating the report
        report = generate_stakeholder_report(request.user)
        
        if isinstance(report, str) and report.startswith('Error'):
            return JsonResponse({'error': report}, status=400)
        
        # Get stats for charts
        from .models import Stakeholder
        stakeholders = Stakeholder.objects.filter(created_by=request.user)
        
        stats = {
            'total': stakeholders.count(),
            'high_influence': stakeholders.filter(influence_level='High').count(),
            'high_interest': stakeholders.filter(interest_level='High').count(),
            'manage_closely': sum(1 for s in stakeholders if s.get_quadrant() == "Manage Closely"),
            'keep_satisfied': sum(1 for s in stakeholders if s.get_quadrant() == "Keep Satisfied"),
            'keep_informed': sum(1 for s in stakeholders if s.get_quadrant() == "Keep Informed"),
            'monitor': sum(1 for s in stakeholders if s.get_quadrant() == "Monitor"),
            'engagement_gaps': sum(1 for s in stakeholders if s.get_desired_engagement_level_value() > s.get_engagement_level_value())
        }
        
        return JsonResponse({'report': report, 'stats': stats})
    else:
        # Render the template for the report page
        return render(request, 'stakeholders/generate_report.html', {
            'title': 'AI-Generated Stakeholder Report'
        })


@login_required
def activity_feed(request):
    """Display activity feed for user's stakeholders"""
    activities = Activity.objects.filter(user=request.user).order_by('-timestamp')[:50]
    
    return render(request, 'stakeholders/activity_feed.html', {
        'activities': activities,
        'title': 'Activity Feed'
    })


@login_required
def tag_list(request):
    """Display all tags"""
    tags = Tag.objects.filter(created_by=request.user)
    
    return render(request, 'stakeholders/tag_list.html', {
        'tags': tags,
        'title': 'Tag Management'
    })


@login_required
def create_tag(request):
    """Create a new tag"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        color = request.POST.get('color', '#007bff')
        
        if not name:
            messages.error(request, 'Tag name is required.')
            return redirect('tag_list')
        
        # Check for duplicate tag names
        if Tag.objects.filter(name=name, created_by=request.user).exists():
            messages.error(request, f'Tag "{name}" already exists.')
            return redirect('tag_list')
        
        # Create the tag
        tag = Tag.objects.create(
            name=name,
            color=color,
            created_by=request.user
        )
        
        messages.success(request, f'Tag "{name}" created successfully.')
        return redirect('tag_list')
    
    return render(request, 'stakeholders/tag_form.html', {
        'title': 'Create Tag'
    })


@login_required
def delete_tag(request, pk):
    """Delete a tag"""
    tag = get_object_or_404(Tag, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        tag_name = tag.name
        tag.delete()
        messages.success(request, f'Tag "{tag_name}" deleted successfully.')
        return redirect('tag_list')
    
    return render(request, 'stakeholders/tag_confirm_delete.html', {
        'tag': tag,
        'title': 'Delete Tag'
    })


@login_required
def add_tag_to_stakeholder(request, stakeholder_id):
    """Add a tag to a stakeholder"""
    stakeholder = get_object_or_404(Stakeholder, pk=stakeholder_id, created_by=request.user)
    
    if request.method == 'POST':
        tag_ids = request.POST.getlist('tags')
        
        # Get the tags
        tags = Tag.objects.filter(id__in=tag_ids, created_by=request.user)
        
        # Add the tags to the stakeholder
        for tag in tags:
            stakeholder.tags.add(tag)
            
            # Log activity
            Activity.objects.create(
                user=request.user,
                activity_type='tag_added',
                stakeholder_name=stakeholder.name,
                stakeholder_id=stakeholder.id,
                description=f'Added tag "{tag.name}" to {stakeholder.name}'
            )
        
        messages.success(request, f'Tags added to {stakeholder.name} successfully.')
        return redirect('stakeholder_detail', pk=stakeholder_id)
    
    # Get the stakeholder's current tags
    current_tags = stakeholder.tags.all()
    
    # Get all tags created by the user that aren't already assigned to the stakeholder
    available_tags = Tag.objects.filter(created_by=request.user).exclude(id__in=[tag.id for tag in current_tags])
    
    return render(request, 'stakeholders/add_tags.html', {
        'stakeholder': stakeholder,
        'available_tags': available_tags,
        'title': f'Add Tags to {stakeholder.name}'
    })


@login_required
def remove_tag_from_stakeholder(request, stakeholder_id, tag_id):
    """Remove a tag from a stakeholder"""
    stakeholder = get_object_or_404(Stakeholder, pk=stakeholder_id, created_by=request.user)
    tag = get_object_or_404(Tag, pk=tag_id, created_by=request.user)
    
    if stakeholder.tags.filter(id=tag.id).exists():
        stakeholder.tags.remove(tag)
        
        # Log activity
        Activity.objects.create(
            user=request.user,
            activity_type='tag_removed',
            stakeholder_name=stakeholder.name,
            stakeholder_id=stakeholder.id,
            description=f'Removed tag "{tag.name}" from {stakeholder.name}'
        )
        
        messages.success(request, f'Tag "{tag.name}" removed from {stakeholder.name} successfully.')
    
    return redirect('stakeholder_detail', pk=stakeholder_id)


@login_required
def relationship_list(request):
    """Display all relationships"""
    relationships = StakeholderRelationship.objects.filter(created_by=request.user)
    
    return render(request, 'stakeholders/relationship_list.html', {
        'relationships': relationships,
        'title': 'Stakeholder Relationships'
    })


@login_required
def create_relationship(request):
    """Create a new relationship between stakeholders"""
    stakeholders = Stakeholder.objects.filter(created_by=request.user)
    
    if request.method == 'POST':
        from_stakeholder_id = request.POST.get('from_stakeholder')
        to_stakeholder_id = request.POST.get('to_stakeholder')
        relationship_type = request.POST.get('relationship_type')
        strength = request.POST.get('strength')
        notes = request.POST.get('notes', '')
        
        # Validate inputs
        if from_stakeholder_id == to_stakeholder_id:
            messages.error(request, 'A stakeholder cannot have a relationship with themselves.')
            return redirect('create_relationship')
        
        from_stakeholder = get_object_or_404(Stakeholder, pk=from_stakeholder_id, created_by=request.user)
        to_stakeholder = get_object_or_404(Stakeholder, pk=to_stakeholder_id, created_by=request.user)
        
        # Check for existing relationship of this type
        if StakeholderRelationship.objects.filter(
            from_stakeholder=from_stakeholder,
            to_stakeholder=to_stakeholder,
            relationship_type=relationship_type
        ).exists():
            messages.error(request, 'This relationship already exists.')
            return redirect('relationship_list')
        
        # Create the relationship
        relationship = StakeholderRelationship.objects.create(
            from_stakeholder=from_stakeholder,
            to_stakeholder=to_stakeholder,
            relationship_type=relationship_type,
            strength=strength,
            notes=notes,
            created_by=request.user
        )
        
        # Log activity
        Activity.objects.create(
            user=request.user,
            activity_type='relationship_added',
            stakeholder_name=from_stakeholder.name,
            stakeholder_id=from_stakeholder.id,
            description=f'Added relationship: {from_stakeholder.name} {relationship.get_relationship_type_display()} {to_stakeholder.name}'
        )
        
        messages.success(request, 'Relationship created successfully.')
        return redirect('relationship_list')
    
    return render(request, 'stakeholders/relationship_form.html', {
        'stakeholders': stakeholders,
        'relationship_types': StakeholderRelationship.RELATIONSHIP_TYPES,
        'title': 'Create Relationship'
    })


@login_required
def delete_relationship(request, pk):
    """Delete a relationship"""
    relationship = get_object_or_404(StakeholderRelationship, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        from_name = relationship.from_stakeholder.name
        to_name = relationship.to_stakeholder.name
        relationship_type = relationship.get_relationship_type_display()
        
        relationship.delete()
        
        messages.success(request, f'Relationship "{from_name} {relationship_type} {to_name}" deleted successfully.')
        return redirect('relationship_list')
    
    return render(request, 'stakeholders/relationship_confirm_delete.html', {
        'relationship': relationship,
        'title': 'Delete Relationship'
    })


@login_required
def stakeholder_network(request):
    """Display network visualization of stakeholder relationships"""
    relationships = StakeholderRelationship.objects.filter(created_by=request.user)
    stakeholders = Stakeholder.objects.filter(created_by=request.user)
    
    # Prepare data for network visualization
    nodes = []
    for stakeholder in stakeholders:
        nodes.append({
            'id': stakeholder.id,
            'name': stakeholder.name,
            'role': stakeholder.role,
            'organization': stakeholder.organization,
            'influence': stakeholder.get_influence_value(),
            'interest': stakeholder.get_interest_value(),
            'quadrant': stakeholder.get_quadrant(),
        })
    
    links = []
    for relationship in relationships:
        links.append({
            'source': relationship.from_stakeholder.id,
            'target': relationship.to_stakeholder.id,
            'type': relationship.relationship_type,
            'strength': relationship.strength,
            'label': relationship.get_relationship_type_display(),
        })
    
    return render(request, 'stakeholders/stakeholder_network.html', {
        'nodes_json': json.dumps(nodes),
        'links_json': json.dumps(links),
        'title': 'Stakeholder Network'
    })