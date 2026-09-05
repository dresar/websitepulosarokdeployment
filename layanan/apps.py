from django.apps import AppConfig


class LayananConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'layanan'
    verbose_name = 'Layanan Desa'
    
    def ready(self):
        # Import signal handlers if needed
        pass


