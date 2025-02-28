# Add this to a new file stakeholders/tasks.py

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from django.db.models import Max, F
from datetime import timedelta
from .models import Stakeholder
from django.contrib.auth.models import User

def send_engagement_reminders():
    """
    Check for stakeholders with no recent engagement and send reminders.
    This function can be run using a scheduled task (e.g., using Celery or Django Q).
    """
    # Define what "recent" means (e.g., 30 days)
    recent_threshold = timezone.now() - timedelta(days=30)
    
    # For each user
    for user in User.objects.all():
        # Skip users without email
        if not user.email:
            continue
            
        # Get all stakeholders for this user
        stakeholders = Stakeholder.objects.filter(created_by=user)
        
        # Stakeholders needing attention
        needs_attention = []
        
        for stakeholder in stakeholders:
            # Get most recent engagement, if any
            latest_engagement = stakeholder.engagements.aggregate(
                latest=Max('date')
            )['latest']
            
            # If no engagement or last engagement older than threshold
            if not latest_engagement or latest_engagement < recent_threshold.date():
                # Also consider high influence stakeholders more important
                priority = 'high' if stakeholder.influence_level == 'High' else 'normal'
                
                # Calculate days since last engagement
                if latest_engagement:
                    days_since = (timezone.now().date() - latest_engagement).days
                else:
                    days_since = None
                
                needs_attention.append({
                    'stakeholder': stakeholder,
                    'days_since': days_since,
                    'priority': priority
                })
        
        # If there are stakeholders needing attention, send an email
        if needs_attention:
            # Sort by priority and days since last engagement
            needs_attention.sort(
                key=lambda x: (0 if x['priority'] == 'high' else 1, 
                              x['days_since'] if x['days_since'] else 999),
                reverse=True
            )
            
            # Prepare email content
            context = {
                'user': user,
                'stakeholders': needs_attention,
                'app_url': settings.APP_URL,  # You'll need to add this to settings.py
            }
            
            # Render the email template
            html_message = render_to_string('stakeholders/email/engagement_reminder.html', context)
            plain_message = render_to_string('stakeholders/email/engagement_reminder_plain.html', context)
            
            # Send the email
            send_mail(
                subject='Stakeholder Engagement Reminder',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )


def send_upcoming_engagement_reminders():
    """
    Send reminders about upcoming desired engagement levels.
    Helps users proactively manage their engagement strategies.
    """
    # Get all stakeholders where desired_engagement > engagement_strategy
    stakeholders_to_improve = Stakeholder.objects.exclude(
        desired_engagement=F('engagement_strategy')
    )
    
    # Group by user
    user_stakeholders = {}
    for stakeholder in stakeholders_to_improve:
        user = stakeholder.created_by
        if not user.email:
            continue
            
        if user not in user_stakeholders:
            user_stakeholders[user] = []
            
        # Calculate engagement gap
        current_level = stakeholder.get_engagement_level_value()
        desired_level = stakeholder.get_desired_engagement_level_value()
        
        user_stakeholders[user].append({
            'stakeholder': stakeholder,
            'current_level': stakeholder.engagement_strategy,
            'desired_level': stakeholder.desired_engagement,
            'gap': desired_level - current_level
        })
    
    # Send emails
    for user, stakeholders in user_stakeholders.items():
        if not stakeholders:
            continue
            
        # Sort by gap (largest first)
        stakeholders.sort(key=lambda x: x['gap'], reverse=True)
        
        # Prepare email content
        context = {
            'user': user,
            'stakeholders': stakeholders,
            'app_url': settings.APP_URL,
        }
        
        # Render the email template
        html_message = render_to_string('stakeholders/email/engagement_upgrade_reminder.html', context)
        plain_message = render_to_string('stakeholders/email/engagement_upgrade_reminder_plain.html', context)
        
        # Send the email
        send_mail(
            subject='Stakeholder Engagement Improvement Opportunities',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )