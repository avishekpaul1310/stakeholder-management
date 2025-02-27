# stakeholders/migrations/0003_stakeholder_desired_engagement.py

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stakeholders', '0002_stakeholder_interest_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='stakeholder',
            name='desired_engagement',
            field=models.CharField(choices=[('Inform', 'Inform'), ('Consult', 'Consult'), ('Involve', 'Involve'), ('Collaborate', 'Collaborate'), ('Empower', 'Empower')], default='Inform', max_length=20),
        ),
    ]