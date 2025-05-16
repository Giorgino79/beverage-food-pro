from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    """Crea i gruppi predefiniti con le relative autorizzazioni dopo la migrazione"""
    # Esegui solo se l'app è dipendenti
    if sender.name != 'dipendenti':
        return
    
    # Crea i gruppi predefiniti
    groups = {
        'Totale': 'Amministratore con accesso completo',
        'Contabile': 'Accesso a tutte le funzioni contabili e anagrafiche',
        'Operativo': 'Accesso alle funzioni operative',
        'Operatore': 'Accesso limitato alle proprie funzioni',
        'Rappresentante': 'Accesso alle funzioni commerciali'
    }
    
    for group_name, description in groups.items():
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            print(f"Gruppo '{group_name}' creato")

    # Assegna permessi per il gruppo Totale
    totale_group = Group.objects.get(name='Totale')
    # Aggiungi tutti i permessi
    all_perms = Permission.objects.all()
    totale_group.permissions.set(all_perms)
    
    # Assegna permessi per il gruppo Contabile
    contabile_group = Group.objects.get(name='Contabile')
    
    # Ottieni i content type per le app rilevanti
    dipendenti_ct = ContentType.objects.get_for_model(apps.get_model('dipendenti', 'Dipendente'))
    anagrafica_ct = ContentType.objects.filter(app_label='anagrafica')
    
    # Ottieni i permessi per queste app
    contabile_perms = Permission.objects.filter(content_type__in=[dipendenti_ct, *anagrafica_ct])
    contabile_group.permissions.set(contabile_perms)
    
    # Assegnazione simile per gli altri gruppi...
    # ...