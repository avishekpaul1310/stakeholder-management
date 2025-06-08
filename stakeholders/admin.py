from django.contrib import admin
from .models import (
    Stakeholder, Engagement, Tag, StakeholderRelationship, 
    Activity, StakeholderInsight, StakeholderReminder
)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'created_by')
    search_fields = ('name',)

@admin.register(Stakeholder)
class StakeholderAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'organization', 'influence_level', 'interest_level', 'get_quadrant')
    list_filter = ('influence_level', 'interest_level', 'engagement_strategy', 'desired_engagement')
    search_fields = ('name', 'role', 'organization', 'email', 'notes')
    filter_horizontal = ('tags',)

@admin.register(Engagement)
class EngagementAdmin(admin.ModelAdmin):
    list_display = ('stakeholder', 'date', 'communication_channel', 'follow_up_required', 'follow_up_completed')
    list_filter = ('date', 'communication_channel', 'follow_up_required', 'follow_up_completed')
    search_fields = ('stakeholder__name', 'description', 'outcome')
    date_hierarchy = 'date'

@admin.register(StakeholderRelationship)
class StakeholderRelationshipAdmin(admin.ModelAdmin):
    list_display = ('from_stakeholder', 'relationship_type', 'to_stakeholder', 'strength')
    list_filter = ('relationship_type', 'strength')
    search_fields = ('from_stakeholder__name', 'to_stakeholder__name', 'notes')

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'stakeholder_name', 'timestamp')
    list_filter = ('activity_type', 'timestamp', 'user')
    search_fields = ('stakeholder_name', 'description')
    date_hierarchy = 'timestamp'

@admin.register(StakeholderInsight)
class StakeholderInsightAdmin(admin.ModelAdmin):
    list_display = ('stakeholder', 'confidence_score', 'is_helpful', 'created_at')
    list_filter = ('is_helpful', 'created_at')
    search_fields = ('stakeholder__name', 'insight_text')

@admin.register(StakeholderReminder)
class StakeholderReminderAdmin(admin.ModelAdmin):
    list_display = ('title', 'stakeholder', 'reminder_type', 'due_date', 'is_completed')
    list_filter = ('reminder_type', 'is_completed', 'due_date')
    search_fields = ('stakeholder__name', 'title', 'description')
    date_hierarchy = 'due_date'
