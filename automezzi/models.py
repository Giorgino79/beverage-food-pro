from django.db import models
from django.conf import settings

def libretto_upload_path(instance, filename):
    return f"automezzi/libretti/{instance.targa}/{filename}"

def assicurazione_upload_path(instance, filename):
    return f"automezzi/assicurazioni/{instance.targa}/{filename}"

def scontrino_upload_path(instance, filename):
    return f"automezzi/rifornimenti/{instance.automezzo.targa}/scontrini/{filename}"

def allegati_manutenzione_path(instance, filename):
    return f"automezzi/manutenzioni/{instance.automezzo.targa}/allegati/{filename}"

def allegato_evento_path(instance, filename):
    return f"automezzi/eventi/{instance.automezzo.targa}/{filename}"

class Automezzo(models.Model):
    targa = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50)
    modello = models.CharField(max_length=50)
    anno_immatricolazione = models.PositiveIntegerField()
    chilometri_attuali = models.PositiveIntegerField(default=0)
    attivo = models.BooleanField(default=True)
    disponibile = models.BooleanField(default=True)
    bloccata = models.BooleanField(default=False)
    motivo_blocco = models.TextField(blank=True, null=True)
    libretto_fronte = models.ImageField(upload_to=libretto_upload_path, blank=True, null=True, help_text="Fronte del libretto di circolazione")
    libretto_retro = models.ImageField(upload_to=libretto_upload_path, blank=True, null=True, help_text="Retro del libretto di circolazione")
    assicurazione = models.FileField(upload_to=assicurazione_upload_path, blank=True, null=True, help_text="File della polizza assicurativa")
    data_revisione = models.DateField(blank=True, null=True, help_text="Data ultima revisione")
    assegnato_a = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='automezzi_assegnati'
    )

    def __str__(self):
        return f"{self.targa} - {self.marca} {self.modello}"

    @property
    def eta(self):
        from datetime import date
        return date.today().year - self.anno_immatricolazione

    def manutenzioni_count(self):
        return self.manutenzioni.count()

    def rifornimenti_count(self):
        return self.rifornimenti.count()

    def eventi_count(self):
        return self.eventi.count()

class Manutenzione(models.Model):
    automezzo = models.ForeignKey(Automezzo, on_delete=models.CASCADE, related_name='manutenzioni')
    data = models.DateField()
    descrizione = models.CharField(max_length=255)
    costo = models.DecimalField(max_digits=8, decimal_places=2)
    completata = models.BooleanField(default=False)
    responsabile = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    allegati = models.FileField(upload_to=allegati_manutenzione_path, blank=True, null=True, help_text="Allegati della manutenzione (fatture, ricevute ecc.)")

    def __str__(self):
        return f"{self.automezzo} - {self.data} - {self.descrizione}"

class Rifornimento(models.Model):
    automezzo = models.ForeignKey(Automezzo, on_delete=models.CASCADE, related_name='rifornimenti')
    data = models.DateField()
    litri = models.DecimalField(max_digits=6, decimal_places=2)
    costo_totale = models.DecimalField(max_digits=7, decimal_places=2)
    chilometri = models.PositiveIntegerField(help_text="Chilometraggio al momento del rifornimento")
    scontrino = models.ImageField(upload_to=scontrino_upload_path, blank=True, null=True, help_text="Foto dello scontrino del rifornimento")

    def __str__(self):
        return f"{self.automezzo} - {self.data} - {self.litri}L"

class EventoAutomezzo(models.Model):
    TIPO_EVENTO_CHOICES = [
        ('incidente', 'Incidente'),
        ('furto', 'Furto'),
        ('fermo', 'Fermo amministrativo'),
        ('guasto', 'Guasto/avaria'),
        ('altro', 'Altro'),
    ]

    automezzo = models.ForeignKey(Automezzo, on_delete=models.CASCADE, related_name='eventi')
    tipo = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES)
    data_evento = models.DateField()
    descrizione = models.TextField(blank=True)
    costo = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    dipendente_coinvolto = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='eventi_coinvolto'
    )
    file_allegato = models.FileField(upload_to=allegato_evento_path, blank=True, null=True, help_text="Foto, verbali, documenti relativi all'evento")
    risolto = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.automezzo} - {self.get_tipo_display()} - {self.data_evento}"