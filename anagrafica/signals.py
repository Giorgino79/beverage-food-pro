from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in
from .models import Rappresentante, Cliente, Fornitore


User = get_user_model()


@receiver(post_save, sender=Rappresentante)
def handle_rappresentante_created(sender, instance, created, **kwargs):
    """
    Gestisce la creazione di un nuovo rappresentante
    """
    if created:
        # Notifica agli amministratori la creazione di un nuovo rappresentante
        admin_users = User.objects.filter(is_staff=True, email__isnull=False)
        admin_emails = [user.email for user in admin_users if user.email]
        
        if admin_emails and hasattr(settings, 'EMAIL_HOST_USER'):
            subject = f'Nuovo Rappresentante Creato: {instance.nome}'
            message = f"""
            Un nuovo rappresentante è stato creato nel sistema:
            
            Nome: {instance.nome}
            Ragione Sociale: {instance.ragione_sociale}
            Email: {instance.email}
            Telefono: {instance.telefono}
            Zona: {instance.zona or 'Non specificata'}
            
            Utente associato: {instance.user.get_full_name() if instance.user else 'Nessuno'}
            
            Per visualizzare i dettagli, accedere al sistema di gestione.
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    admin_emails,
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Errore invio email: {e}")


@receiver(post_save, sender=Cliente)
def handle_cliente_created(sender, instance, created, **kwargs):
    """
    Gestisce la creazione/modifica di un cliente
    """
    if created and instance.rappresentante:
        # Notifica al rappresentante la creazione di un nuovo cliente
        if (instance.rappresentante.user and 
            instance.rappresentante.user.email and 
            hasattr(settings, 'EMAIL_HOST_USER')):
            
            subject = f'Nuovo Cliente Assegnato: {instance.ragione_sociale}'
            message = f"""
            Ciao {instance.rappresentante.nome},
            
            Ti è stato assegnato un nuovo cliente:
            
            Ragione Sociale: {instance.ragione_sociale}
            Città: {instance.città}
            Email: {instance.email}
            Telefono: {instance.telefono}
            
            Puoi visualizzare i dettagli accedendo al sistema.
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [instance.rappresentante.user.email],
                    fail_silently=True,
                )
            except Exception:
                pass


@receiver(pre_delete, sender=Rappresentante)
def handle_rappresentante_deletion(sender, instance, **kwargs):
    """
    Gestisce l'eliminazione di un rappresentante
    """
    # Verifica se ha clienti associati
    clienti_count = instance.clienti.count()
    if clienti_count > 0:
        # Questo segnale viene chiamato ma l'eliminazione procede comunque
        # Il controllo principale dovrebbe essere nelle views
        print(f"Attenzione: Eliminando rappresentante {instance.nome} con {clienti_count} clienti associati")


@receiver(user_logged_in)
def check_rappresentante_profile(sender, user, request, **kwargs):
    """
    Controlla se un rappresentante ha completato il suo profilo al login
    """
    try:
        rappresentante = Rappresentante.objects.get(user=user)
        
        # Lista dei campi da verificare
        required_fields = ['partita_iva', 'codice_fiscale', 'telefono', 'email']
        missing_fields = []
        
        for field in required_fields:
            if not getattr(rappresentante, field):
                missing_fields.append(field)
        
        if missing_fields:
            messages.warning(
                request,
                f"Completa il tuo profilo rappresentante. Campi mancanti: {', '.join(missing_fields)}"
            )
    except Rappresentante.DoesNotExist:
        # L'utente non è un rappresentante
        pass


# Segnali per logging delle operazioni
@receiver(post_save, sender=Cliente)
@receiver(post_save, sender=Fornitore)
@receiver(post_save, sender=Rappresentante)
def log_anagrafica_operations(sender, instance, created, **kwargs):
    """
    Registra le operazioni sull'anagrafica per audit
    """
    if hasattr(settings, 'ANAGRAFICA_LOG_FILE'):
        import logging
        import os
        
        # Configurazione del logger
        logger = logging.getLogger('anagrafica_operations')
        if not logger.handlers:
            handler = logging.FileHandler(settings.ANAGRAFICA_LOG_FILE)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        
        # Log dell'operazione
        operation = 'CREATED' if created else 'UPDATED'
        model_name = sender.__name__
        
        if hasattr(instance, 'nome'):
            identifier = instance.nome
        elif hasattr(instance, 'ragione_sociale'):
            identifier = instance.ragione_sociale
        else:
            identifier = str(instance.id)
        
        logger.info(f"{operation} {model_name}: {identifier}")


# Segnali per sincronizzazione zone
@receiver(post_save, sender=Rappresentante)
def sync_cliente_zone(sender, instance, **kwargs):
    """
    Sincronizza la zona dai clienti quando viene modificata sul rappresentante
    """
    if not kwargs.get('created', False) and instance.zona:
        # Aggiorna la zona di tutti i clienti del rappresentante se non specificata
        instance.clienti.filter(zona__isnull=True).update(zona=instance.zona)


# Segnali per validazioni aggiuntive
@receiver(post_save, sender=Cliente)
def validate_cliente_rappresentante_zone(sender, instance, **kwargs):
    """
    Valida che cliente e rappresentante siano nella stessa zona
    """
    if (instance.rappresentante and 
        instance.rappresentante.zona and 
        instance.zona and 
        instance.rappresentante.zona != instance.zona):
        
        # Log del warning
        import logging
        logger = logging.getLogger('anagrafica_warnings')
        logger.warning(
            f"Cliente {instance.ragione_sociale} in zona {instance.zona} "
            f"assegnato a rappresentante {instance.rappresentante.nome} "
            f"in zona {instance.rappresentante.zona}"
        )