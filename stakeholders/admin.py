from django.contrib import admin
from .models import Stakeholder

@admin.register(Stakeholder)
class StakeholderAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'role', 'organization', 'created_at')
    search_fields = ('name', 'email', 'role', 'organization')
    list_filter = ('role', 'created_at')