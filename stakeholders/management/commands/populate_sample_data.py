# stakeholders/management/commands/populate_sample_data.py

import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from stakeholders.models import (
    Tag, Stakeholder, Engagement, StakeholderRelationship, 
    Activity, StakeholderInsight, StakeholderReminder
)

class Command(BaseCommand):
    help = 'Populate database with sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            default='admin',
            help='Username of the user for whom to create sample data',
        )

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" does not exist'))
            self.stdout.write(self.style.WARNING('Creating a superuser with username "admin" and password "admin"'))
            
            # Create a user if one doesn't exist
            user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin'
            )
        
        # Create tags
        self.create_tags(user)
        
        # Create stakeholders
        stakeholders = self.create_stakeholders(user)
        
        # Add tags to stakeholders
        self.add_tags_to_stakeholders(stakeholders, user)
        
        # Create stakeholder relationships
        self.create_relationships(stakeholders, user)
        
        # Create engagements
        self.create_engagements(stakeholders, user)
        
        # Create insights
        self.create_insights(stakeholders, user)
        
        # Create reminders
        self.create_reminders(stakeholders, user)
        
        # Create some activities (some are created automatically when other objects are created)
        self.create_activities(stakeholders, user)
        
        self.stdout.write(self.style.SUCCESS('Successfully populated database with sample data'))
    
    def create_tags(self, user):
        tag_data = [
            {"name": "Executive", "color": "#dc3545"},  # red
            {"name": "Technical", "color": "#007bff"},  # blue
            {"name": "Finance", "color": "#28a745"},    # green
            {"name": "Marketing", "color": "#fd7e14"},  # orange
            {"name": "HR", "color": "#6610f2"},         # purple
            {"name": "Legal", "color": "#6c757d"},      # gray
            {"name": "Operations", "color": "#17a2b8"}, # cyan
            {"name": "External", "color": "#e83e8c"},   # pink
            {"name": "Internal", "color": "#ffc107"},   # yellow
            {"name": "High Priority", "color": "#dc3545"}, # red
        ]
        
        tags = []
        for tag in tag_data:
            tag_obj, created = Tag.objects.get_or_create(
                name=tag['name'], 
                defaults={
                    'color': tag['color'],
                    'created_by': user
                }
            )
            if created:
                self.stdout.write(f"Created tag: {tag['name']}")
            tags.append(tag_obj)
            
        return tags
    
    def create_stakeholders(self, user):
        stakeholder_data = [
            {
                "name": "John Smith", 
                "role": "CEO", 
                "organization": "ABC Corporation",
                "email": "john.smith@abccorp.example",
                "phone": "+1-555-123-4567", 
                "influence_level": "High",
                "interest_level": "High",
                "engagement_strategy": "Collaborate", 
                "desired_engagement": "Empower",
                "notes": "Key decision maker, has final say on budget approval."
            },
            {
                "name": "Alice Johnson", 
                "role": "CTO", 
                "organization": "ABC Corporation",
                "email": "alice.j@abccorp.example",
                "phone": "+1-555-234-5678", 
                "influence_level": "High",
                "interest_level": "Medium",
                "engagement_strategy": "Consult", 
                "desired_engagement": "Involve",
                "notes": "Technical expert, interested in implementation details."
            },
            {
                "name": "Robert Davis", 
                "role": "CFO", 
                "organization": "ABC Corporation",
                "email": "r.davis@abccorp.example",
                "phone": "+1-555-345-6789", 
                "influence_level": "Medium",
                "interest_level": "Low",
                "engagement_strategy": "Inform", 
                "desired_engagement": "Consult",
                "notes": "Primarily concerned with budget and ROI."
            },
            {
                "name": "Emma Wilson", 
                "role": "Marketing Director", 
                "organization": "ABC Corporation",
                "email": "e.wilson@abccorp.example",
                "phone": "+1-555-456-7890", 
                "influence_level": "Medium",
                "interest_level": "High",
                "engagement_strategy": "Involve", 
                "desired_engagement": "Collaborate",
                "notes": "Focused on how the project affects brand image."
            },
            {
                "name": "Michael Chen", 
                "role": "Project Manager", 
                "organization": "ABC Corporation",
                "email": "m.chen@abccorp.example",
                "phone": "+1-555-567-8901", 
                "influence_level": "Medium",
                "interest_level": "High",
                "engagement_strategy": "Collaborate", 
                "desired_engagement": "Collaborate",
                "notes": "Day-to-day point of contact."
            },
            {
                "name": "Sarah Jackson", 
                "role": "Legal Counsel", 
                "organization": "ABC Corporation",
                "email": "s.jackson@abccorp.example",
                "phone": "+1-555-678-9012", 
                "influence_level": "Low",
                "interest_level": "Medium",
                "engagement_strategy": "Consult", 
                "desired_engagement": "Consult",
                "notes": "Reviews all contracts and legal documents."
            },
            {
                "name": "David Kim", 
                "role": "IT Director", 
                "organization": "XYZ Industries",
                "email": "david.k@xyz.example",
                "phone": "+1-555-789-0123", 
                "influence_level": "High",
                "interest_level": "High",
                "engagement_strategy": "Involve", 
                "desired_engagement": "Collaborate",
                "notes": "Technical expert from partner organization."
            },
            {
                "name": "Jennifer Lee", 
                "role": "HR Director", 
                "organization": "ABC Corporation",
                "email": "j.lee@abccorp.example",
                "phone": "+1-555-890-1234", 
                "influence_level": "Low",
                "interest_level": "Low",
                "engagement_strategy": "Inform", 
                "desired_engagement": "Inform",
                "notes": "Involved in staffing aspects of the project."
            },
            {
                "name": "Carlos Rodriguez", 
                "role": "Operations Manager", 
                "organization": "ABC Corporation",
                "email": "c.rodriguez@abccorp.example",
                "phone": "+1-555-901-2345", 
                "influence_level": "Medium",
                "interest_level": "Medium",
                "engagement_strategy": "Involve", 
                "desired_engagement": "Involve",
                "notes": "Oversees operational impacts of the project."
            },
            {
                "name": "Linda Wong", 
                "role": "Customer Representative", 
                "organization": "Customer Inc.",
                "email": "l.wong@customer.example",
                "phone": "+1-555-012-3456", 
                "influence_level": "High",
                "interest_level": "High",
                "engagement_strategy": "Collaborate", 
                "desired_engagement": "Empower",
                "notes": "Primary customer contact, very engaged in the project."
            }
        ]
        
        stakeholders = []
        for data in stakeholder_data:
            stakeholder, created = Stakeholder.objects.get_or_create(
                name=data['name'],
                role=data['role'],
                organization=data['organization'],
                created_by=user,
                defaults={
                    'email': data['email'],
                    'phone': data['phone'],
                    'influence_level': data['influence_level'],
                    'interest_level': data['interest_level'],
                    'engagement_strategy': data['engagement_strategy'],
                    'desired_engagement': data['desired_engagement'],
                    'notes': data['notes'],
                }
            )
            if created:
                self.stdout.write(f"Created stakeholder: {data['name']}")
            stakeholders.append(stakeholder)
        
        return stakeholders
    
    def add_tags_to_stakeholders(self, stakeholders, user):
        # Get all tags
        tags = list(Tag.objects.all())
        
        for stakeholder in stakeholders:
            # Randomly select 1-3 tags for each stakeholder
            num_tags = random.randint(1, 3)
            selected_tags = random.sample(tags, num_tags)
            
            # Clear existing tags and add new ones
            stakeholder.tags.clear()
            for tag in selected_tags:
                stakeholder.tags.add(tag)
                
                # Create activity for tag_added
                Activity.objects.create(
                    user=user,
                    activity_type='tag_added',
                    stakeholder_name=stakeholder.name,
                    stakeholder_id=stakeholder.id,
                    description=f"Added tag '{tag.name}' to {stakeholder.name}"
                )
                
            self.stdout.write(f"Added {num_tags} tags to {stakeholder.name}")
    
    def create_relationships(self, stakeholders, user):
        # Define some relationship patterns
        relationship_data = [
            # CEO relationships
            {'from_idx': 0, 'to_idx': 1, 'type': 'supervises', 'strength': 3},  # CEO -> CTO
            {'from_idx': 0, 'to_idx': 2, 'type': 'supervises', 'strength': 3},  # CEO -> CFO
            {'from_idx': 0, 'to_idx': 3, 'type': 'supervises', 'strength': 3},  # CEO -> Marketing Director
            
            # CTO relationships
            {'from_idx': 1, 'to_idx': 0, 'type': 'reports_to', 'strength': 3},  # CTO -> CEO
            {'from_idx': 1, 'to_idx': 4, 'type': 'supervises', 'strength': 2},  # CTO -> Project Manager
            {'from_idx': 1, 'to_idx': 6, 'type': 'collaborates', 'strength': 2},  # CTO -> IT Director (XYZ)
            
            # CFO relationships
            {'from_idx': 2, 'to_idx': 0, 'type': 'reports_to', 'strength': 3},  # CFO -> CEO
            {'from_idx': 2, 'to_idx': 5, 'type': 'collaborates', 'strength': 1},  # CFO -> Legal Counsel
            
            # Marketing Director relationships
            {'from_idx': 3, 'to_idx': 0, 'type': 'reports_to', 'strength': 3},  # Marketing Dir -> CEO
            {'from_idx': 3, 'to_idx': 9, 'type': 'collaborates', 'strength': 2},  # Marketing Dir -> Customer Rep
            
            # Project Manager relationships
            {'from_idx': 4, 'to_idx': 1, 'type': 'reports_to', 'strength': 2},  # PM -> CTO
            {'from_idx': 4, 'to_idx': 8, 'type': 'collaborates', 'strength': 3},  # PM -> Operations Manager
            {'from_idx': 4, 'to_idx': 6, 'type': 'collaborates', 'strength': 1},  # PM -> IT Director (XYZ)
            
            # Legal Counsel relationships
            {'from_idx': 5, 'to_idx': 0, 'type': 'reports_to', 'strength': 1},  # Legal -> CEO
            
            # HR Director relationships
            {'from_idx': 7, 'to_idx': 0, 'type': 'reports_to', 'strength': 1},  # HR -> CEO
            
            # Operations Manager relationships
            {'from_idx': 8, 'to_idx': 0, 'type': 'reports_to', 'strength': 2},  # Ops Manager -> CEO
            {'from_idx': 8, 'to_idx': 4, 'type': 'collaborates', 'strength': 3},  # Ops Manager -> PM
            
            # Customer Rep relationships
            {'from_idx': 9, 'to_idx': 3, 'type': 'collaborates', 'strength': 2},  # Customer Rep -> Marketing Dir
            {'from_idx': 9, 'to_idx': 4, 'type': 'influences', 'strength': 3},  # Customer Rep -> PM
        ]
        
        for rel_data in relationship_data:
            try:
                from_stakeholder = stakeholders[rel_data['from_idx']]
                to_stakeholder = stakeholders[rel_data['to_idx']]
                
                relationship, created = StakeholderRelationship.objects.get_or_create(
                    from_stakeholder=from_stakeholder,
                    to_stakeholder=to_stakeholder,
                    relationship_type=rel_data['type'],
                    defaults={
                        'strength': rel_data['strength'],
                        'notes': f"Sample {rel_data['type']} relationship",
                        'created_by': user
                    }
                )
                
                if created:
                    # Create activity record
                    Activity.objects.create(
                        user=user,
                        activity_type='relationship_added',
                        stakeholder_name=from_stakeholder.name,
                        stakeholder_id=from_stakeholder.id,
                        description=f"Added relationship: {from_stakeholder.name} {relationship.get_relationship_type_display()} {to_stakeholder.name}"
                    )
                    
                    self.stdout.write(f"Created relationship: {from_stakeholder.name} {rel_data['type']} {to_stakeholder.name}")
            except IndexError:
                self.stdout.write(self.style.WARNING(f"Could not create relationship: Index out of range"))
    
    def create_engagements(self, stakeholders, user):
        now = timezone.now()
        
        # Generate a range of dates from 30 days ago to 30 days in the future
        start_date = now - timedelta(days=30)
        end_date = now + timedelta(days=30)
        
        # Create 2-5 engagements for each stakeholder
        for stakeholder in stakeholders:
            num_engagements = random.randint(2, 5)
            
            for i in range(num_engagements):
                # Generate a random date within the range
                days_offset = random.randint(-30, 30)
                engagement_date = (now + timedelta(days=days_offset)).date()
                
                # For past engagements, no follow up or follow up completed
                # For future engagements, may have follow up planned
                follow_up_required = days_offset > 0 or (days_offset < 0 and random.choice([True, False]))
                follow_up_completed = days_offset < 0 and follow_up_required and random.choice([True, False])
                
                if follow_up_required and not follow_up_completed:
                    follow_up_date = (engagement_date + timedelta(days=random.randint(7, 14)))
                else:
                    follow_up_date = None
                
                # Generate random satisfaction rating for past engagements
                satisfaction = None
                if days_offset < 0:  # Past engagement
                    satisfaction = random.randint(1, 5)
                
                # Choose a random communication channel
                channel_choices = [c[0] for c in Engagement.COMMUNICATION_CHANNELS]
                comm_channel = random.choice(channel_choices)
                
                engagement = Engagement.objects.create(
                    stakeholder=stakeholder,
                    date=engagement_date,
                    description=f"Sample engagement {i+1} with {stakeholder.name}",
                    outcome="Discussion about project progress and next steps." if days_offset < 0 else "",
                    communication_channel=comm_channel,
                    follow_up_required=follow_up_required,
                    follow_up_date=follow_up_date,
                    follow_up_completed=follow_up_completed,
                    satisfaction_rating=satisfaction,
                    created_by=user
                )
                
                # Create activity record
                Activity.objects.create(
                    user=user,
                    activity_type='engagement',
                    stakeholder_name=stakeholder.name,
                    stakeholder_id=stakeholder.id,
                    description=f"Recorded engagement with {stakeholder.name} on {engagement.date}"
                )
                
                self.stdout.write(f"Created engagement with {stakeholder.name} on {engagement_date}")
    
    def create_insights(self, stakeholders, user):
        # Sample insight templates
        insight_templates = [
            "Based on recent engagements, {name} seems to be primarily concerned with {topic}.",
            "{name}'s interest in the project has {trend} over the past month.",
            "Consider engaging {name} more about {topic} to increase their engagement level.",
            "{name} may be a valuable resource for {topic} based on their background.",
            "There appears to be some tension between {name} and other stakeholders regarding {topic}.",
            "{name} could potentially become a project champion if engaged properly on {topic}.",
            "Recent communications suggest {name} is looking for more involvement in {topic}.",
            "{name}'s feedback patterns indicate they value {topic} more than initially thought."
        ]
        
        topics = [
            "budget constraints", 
            "technical specifications", 
            "timeline concerns", 
            "resource allocation", 
            "strategic alignment",
            "implementation details",
            "risk management",
            "quality assurance",
            "process improvements"
        ]
        
        trends = ["increased", "decreased", "remained stable", "fluctuated"]
        
        # Create 0-3 insights for each stakeholder
        for stakeholder in stakeholders:
            num_insights = random.randint(0, 3)
            
            for i in range(num_insights):
                # Generate a random insight
                template = random.choice(insight_templates)
                topic = random.choice(topics)
                trend = random.choice(trends)
                
                insight_text = template.format(
                    name=stakeholder.name,
                    topic=topic,
                    trend=trend
                )
                
                # Random confidence score between 0.6 and 0.95
                confidence = round(random.uniform(0.6, 0.95), 2)
                
                # Random helpfulness feedback (or None)
                is_helpful = random.choice([True, False, None])
                
                insight = StakeholderInsight.objects.create(
                    stakeholder=stakeholder,
                    insight_text=insight_text,
                    confidence_score=confidence,
                    generated_by=user,
                    is_helpful=is_helpful
                )
                
                # Create activity record
                Activity.objects.create(
                    user=user,
                    activity_type='ai_insight',
                    stakeholder_name=stakeholder.name,
                    stakeholder_id=stakeholder.id,
                    description=f"Generated AI insight for {stakeholder.name}"
                )
                
                self.stdout.write(f"Created insight for {stakeholder.name}")
    
    def create_reminders(self, stakeholders, user):
        now = timezone.now()
        
        # Create 0-2 reminders for each stakeholder
        for stakeholder in stakeholders:
            num_reminders = random.randint(0, 2)
            
            for i in range(num_reminders):
                # Choose a random reminder type
                reminder_type = random.choice([t[0] for t in StakeholderReminder.REMINDER_TYPES])
                
                # Generate due date between now and 14 days from now
                days_offset = random.randint(1, 14)
                due_date = now + timedelta(days=days_offset)
                
                # 30% chance the reminder is completed
                is_completed = random.random() < 0.3
                completed_at = now - timedelta(hours=random.randint(1, 24)) if is_completed else None
                
                # Create title based on reminder type
                if reminder_type == 'follow_up':
                    title = f"Follow up with {stakeholder.name} about project progress"
                elif reminder_type == 'review':
                    title = f"Review {stakeholder.name}'s engagement history"
                elif reminder_type == 'update':
                    title = f"Update {stakeholder.name}'s contact information"
                else:  # meeting
                    title = f"Schedule quarterly review meeting with {stakeholder.name}"
                
                reminder = StakeholderReminder.objects.create(
                    stakeholder=stakeholder,
                    reminder_type=reminder_type,
                    title=title,
                    description=f"Sample reminder for {stakeholder.name}",
                    due_date=due_date,
                    is_completed=is_completed,
                    completed_at=completed_at,
                    created_by=user
                )
                
                self.stdout.write(f"Created {reminder_type} reminder for {stakeholder.name}")
    
    def create_activities(self, stakeholders, user):
        # Most activities are created automatically when other objects are created
        # This method just adds a few extra activities for variety
        
        activity_descriptions = [
            "Reviewed stakeholder matrix",
            "Updated stakeholder contact information",
            "Analyzed stakeholder engagement patterns",
            "Prepared for upcoming stakeholder meeting",
            "Summarized stakeholder feedback"
        ]
        
        # Create 5-10 additional random activities
        num_activities = random.randint(5, 10)
        
        for i in range(num_activities):
            # Choose a random stakeholder
            stakeholder = random.choice(stakeholders)
            
            # Choose a random activity type from a subset
            activity_type = random.choice(['updated', 'engagement'])
            
            # Choose a random description
            description = random.choice(activity_descriptions)
            
            # Generate a random timestamp within the last 7 days
            days_ago = random.randint(0, 7)
            hours_ago = random.randint(0, 23)
            timestamp = timezone.now() - timedelta(days=days_ago, hours=hours_ago)
            
            activity = Activity.objects.create(
                user=user,
                activity_type=activity_type,
                stakeholder_name=stakeholder.name,
                stakeholder_id=stakeholder.id,
                description=description,
                timestamp=timestamp
            )
            
            self.stdout.write(f"Created additional activity: {description} for {stakeholder.name}")
