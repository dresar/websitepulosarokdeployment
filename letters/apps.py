from django.apps import AppConfig


class LettersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'letters'
    verbose_name = 'Letter Management System'
    
    def ready(self):
        """Import signals when app is ready"""
        try:
            import letters.signals
        except ImportError:
            pass
