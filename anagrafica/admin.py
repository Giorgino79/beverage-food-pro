from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AnagraficaConfig(AppConfig):
    """Configurazione dell'app anagrafica"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'anagrafica'
    verbose_name = _('Anagrafica')
    
    def ready(self):
        """Importa i segnali quando l'app è pronta"""
        import anagrafica.signals