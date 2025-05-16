from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import os
from datetime import datetime, timedelta, date

class Dipendente(AbstractUser):
    class Autorizzazioni(models.TextChoices):
        totale = 'totale', _('Amministratore completo')
        contabile = 'contabile', _('Gestione contabilità')
        operativo = 'operativo', _('Gestione operativa')
        operatore = 'operatore', _('Operatore base')
        rappresentante = 'rappresentante', _('Rappresentante commerciale')
    
    # Informazioni personali
    livello = models.CharField(max_length=30, choices=Autorizzazioni.choices, default='operatore', verbose_name=_('Livello autorizzazioni'))
    indirizzo = models.CharField(max_length=500, blank=True, null=True, verbose_name=_('Indirizzo'))
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('Telefono'))
    data_nascita = models.DateField(blank=True, null=True, verbose_name=_('Data di nascita'))
    data_assunzione = models.DateField(blank=True, null=True, verbose_name=_('Data di assunzione'))
    
    # Documenti di identità
    CF = models.CharField(verbose_name=_('Codice Fiscale'), max_length=16, blank=True, null=True)
    carta_d_identità = models.CharField(verbose_name=_("Numero della carta di identità"), max_length=200, blank=True, null=True)
    data_scadenza_ci = models.DateField(verbose_name=_("Scadenza carta identità"), blank=True, null=True)
    patente_di_guida = models.CharField(verbose_name=_("Numero della patente di guida"), max_length=200, blank=True, null=True)
    data_scadenza_patente = models.DateField(verbose_name=_("Scadenza patente"), blank=True, null=True)
    categorie_patente = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('Categorie patente'))
    
    # Posizioni contributive
    posizione_inail = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('Posizione INAIL'))
    posizione_inps = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('Posizione INPS'))
    
    # Media e file
    foto_dipendente = models.ImageField(upload_to='dipendenti/foto', blank=True, null=True, verbose_name=_('Foto dipendente'))
    foto_carta_identità = models.ImageField(upload_to='dipendenti/documenti', blank=True, null=True, verbose_name=_('Foto carta identità'))
    foto_codice_fiscale = models.ImageField(upload_to='dipendenti/documenti', blank=True, null=True, verbose_name=_('Foto codice fiscale'))
    foto_patente = models.ImageField(upload_to='dipendenti/documenti', blank=True, null=True, verbose_name=_('Foto patente'))
    
    # Note
    note = models.TextField(max_length=4000, blank=True, null=True, verbose_name=_('Note'))
    is_online = models.BooleanField(
        _('Online'),
        default=False,
        help_text=_('Indica se il dipendente è attualmente online')
    )
    
    ultimo_accesso = models.DateTimeField(
        _('Ultimo accesso'),
        null=True,
        blank=True
    )
    
    # Metodo per ottenere le iniziali
    def get_initials(self):
        """Restituisce le iniziali del nome e cognome"""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        elif self.first_name:
            return self.first_name[0].upper()
        elif self.last_name:
            return self.last_name[0].upper()
        return self.username[:2].upper()
    
    class Meta:
        verbose_name = _('Dipendente')
        verbose_name_plural = _('Dipendenti')
        ordering = ['username']
    
    def get_absolute_url(self):
        return reverse("dipendenti:vedidipendente", kwargs={"pk": self.pk})
    
    def __str__(self):
        return f'{self.get_full_name() or self.username}'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._assign_groups()
    
    def _assign_groups(self):
        """Metodo interno per assegnare i gruppi in base al livello"""
        if self.pk is not None:
            self.groups.clear()
            mapping = {
                self.Autorizzazioni.totale: 'Totale',
                self.Autorizzazioni.contabile: 'Contabile',
                self.Autorizzazioni.operativo: 'Operativo',
                self.Autorizzazioni.operatore: 'Operatore',
                self.Autorizzazioni.rappresentante: 'Rappresentante',
            }
            if self.livello in mapping:
                group_name = mapping[self.livello]
                group, created = Group.objects.get_or_create(name=group_name)
                self.groups.add(group)


class AllegatoDipendente(models.Model):
    """Modello per gestire gli allegati dei dipendenti in modo più flessibile"""
    
    class TipoAllegato(models.TextChoices):
        CONTRATTO = 'contratto', _('Contratto di lavoro')
        PRIVACY = 'privacy', _('Informativa Privacy')
        SICUREZZA = 'sicurezza', _('Documenti Sicurezza')
        FORMAZIONE = 'formazione', _('Attestati Formazione')
        ALTRO = 'altro', _('Altro documento')
    
    dipendente = models.ForeignKey('dipendenti.Dipendente', on_delete=models.CASCADE, related_name='allegati', verbose_name=_('Dipendente'))
    tipo = models.CharField(max_length=20, choices=TipoAllegato.choices, default='altro', verbose_name=_('Tipo documento'))
    nome = models.CharField(max_length=200, verbose_name=_('Nome documento'))
    file = models.FileField(upload_to='dipendenti/allegati', verbose_name=_('File'))
    data_caricamento = models.DateTimeField(auto_now_add=True, verbose_name=_('Data caricamento'))
    visibile_al_dipendente = models.BooleanField(default=True, verbose_name=_('Visibile al dipendente'))
    note = models.TextField(blank=True, null=True, verbose_name=_('Note'))
    
    class Meta:
        verbose_name = _('Allegato dipendente')
        verbose_name_plural = _('Allegati dipendente')
        ordering = ['-data_caricamento']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nome}"


class Giornata(models.Model):
    data = models.DateField(auto_now_add=True, verbose_name=_('Data'))
    operatore = models.ForeignKey('dipendenti.Dipendente', on_delete=models.CASCADE, related_name='giornate', verbose_name=_('Operatore'))
    
    # Orari di lavoro
    ora_inizio_mattina = models.TimeField(blank=True, null=True, verbose_name=_('Inizio mattina'))
    ora_fine_mattina = models.TimeField(blank=True, null=True, verbose_name=_('Fine mattina'))
    ora_inizio_pomeriggio = models.TimeField(blank=True, null=True, verbose_name=_('Inizio pomeriggio'))
    ora_fine_pomeriggio = models.TimeField(blank=True, null=True, verbose_name=_('Fine pomeriggio'))
    
    # Gestione assenze
    class TipoAssenza(models.TextChoices):
        NESSUNA = 'nessuna', _('Nessuna assenza')
        FERIE = 'ferie', _('Ferie')
        MALATTIA = 'malattia', _('Malattia')
        PERMESSO = 'permesso', _('Permesso')
        ALTRO = 'altro', _('Altro')
    
    assenza = models.CharField(max_length=20, choices=TipoAssenza.choices, default='nessuna', verbose_name=_('Tipo assenza'))
    nota_assenza = models.TextField(blank=True, null=True, verbose_name=_('Note assenza'))
    
    # Veicolo assegnato - Da aggiungere quando verrà creata l'app automezzi
    # mezzo = models.ForeignKey('automezzi.Automezzo', on_delete=models.SET_NULL, null=True, 
    #                           blank=True, related_name='giornate_uso', verbose_name=_('Mezzo assegnato'))
    
    # Chiusura giornata
    chiudi_giornata = models.BooleanField(default=False, verbose_name=_('Giornata chiusa'))
    confermata = models.BooleanField(default=False, verbose_name=_('Confermata'))
    confermata_da = models.ForeignKey('dipendenti.Dipendente', on_delete=models.SET_NULL, null=True, blank=True, 
                                      related_name='giornate_confermate', verbose_name=_('Confermata da'))
    
    class Meta:
        verbose_name = _('Giornata lavorativa')
        verbose_name_plural = _('Giornate lavorative')
        unique_together = ('operatore', 'data')
        ordering = ['-data']
    
    def __str__(self):
        return f'{self.data} - {self.operatore}'
    
    def daily_hours(self):
        """Calcola le ore lavorate nella giornata"""
        total = timedelta()
        today_date = self.data  # Usa la data dell'oggetto anziché la data corrente
        
        # Calcolo ore mattina
        if self.ora_inizio_mattina and self.ora_fine_mattina:
            inizio = datetime.combine(today_date, self.ora_inizio_mattina)
            fine = datetime.combine(today_date, self.ora_fine_mattina)
            if fine > inizio:  # Verifica che l'orario di fine sia dopo l'inizio
                total += (fine - inizio)
        
        # Calcolo ore pomeriggio
        if self.ora_inizio_pomeriggio and self.ora_fine_pomeriggio:
            inizio = datetime.combine(today_date, self.ora_inizio_pomeriggio)
            fine = datetime.combine(today_date, self.ora_fine_pomeriggio)
            if fine > inizio:  # Verifica che l'orario di fine sia dopo l'inizio
                total += (fine - inizio)
        
        # Caso speciale: solo inizio mattina e fine pomeriggio (giornata continuativa)
        if (self.ora_inizio_mattina and self.ora_fine_pomeriggio and 
            not self.ora_fine_mattina and not self.ora_inizio_pomeriggio):
            inizio = datetime.combine(today_date, self.ora_inizio_mattina)
            fine = datetime.combine(today_date, self.ora_fine_pomeriggio)
            if fine > inizio:
                total = (fine - inizio)
        
        return total