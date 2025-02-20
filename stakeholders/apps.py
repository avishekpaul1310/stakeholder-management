from django.apps import AppConfig

class StakeholdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stakeholders'

    def ready(self):
        pass  # Remove signals import if not using Django signals