from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class DipendentiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dipendenti'
    verbose_name = _('Gestione Dipendenti')
    
    def ready(self):
        """Eseguito quando l'app è pronta"""
        # Import dei segnali se necessario
        # import dipendenti.signals