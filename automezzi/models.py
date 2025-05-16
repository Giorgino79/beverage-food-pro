# automezzi/models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from datetime import date
from decimal import Decimal
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class TipoCarburante(models.Model):
    """Modello per i tipi di carburante"""
    nome = models.CharField(max_length=50, unique=True, help_text="Es: Benzina, Diesel, GPL, Metano")
    costo_per_litro = models.DecimalField(max_digits=6, decimal_places=3, default=0.000)
    
    class Meta:
        verbose_name = "Tipo Carburante"
        verbose_name_plural = "Tipi Carburante"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - €{self.costo_per_litro}/L"


class Automezzo(models.Model):
    """Modello principale per la gestione degli automezzi"""
    
    # Dati base del veicolo
    targa = models.CharField(max_length=10, unique=True, help_text="Targa del veicolo")
    marca = models.CharField(max_length=100)
    modello = models.CharField(max_length=100)
    anno_immatricolazione = models.PositiveIntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(date.today().year + 1)]
    )
    
    # Dati tecnici
    numero_telaio = models.CharField(max_length=50, unique=True, blank=True, null=True)
    tipo_carburante = models.ForeignKey(TipoCarburante, on_delete=models.PROTECT)
    cilindrata = models.PositiveIntegerField(blank=True, null=True, help_text="in cc")
    potenza = models.PositiveIntegerField(blank=True, null=True, help_text="in CV")
    
    # Chilometraggio
    chilometri_iniziali = models.PositiveIntegerField(default=0, help_text="Km all'acquisto")
    chilometri_attuali = models.PositiveIntegerField(default=0, help_text="Km attuali")
    
    # Dati di acquisto
    data_acquisto = models.DateField(blank=True, null=True)
    costo_acquisto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Assegnazione
    assegnato_a = models.ForeignKey(
        'dipendenti.Dipendente', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='automezzi_assegnati'
    )
    
    # Stato
    attivo = models.BooleanField(default=True)
    disponibile = models.BooleanField(default=True)
    note = models.TextField(blank=True, null=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Automezzo"
        verbose_name_plural = "Automezzi"
        ordering = ['targa']
    
    def __str__(self):
        return f"{self.targa} - {self.marca} {self.modello}"
    
    def get_absolute_url(self):
        return reverse('automezzi:dettaglio', kwargs={'pk': self.pk})
    
    @property
    def chilometri_totali(self):
        """Calcola i chilometri totali percorsi"""
        return self.chilometri_attuali - self.chilometri_iniziali
    
    @property
    def eta(self):
        """Calcola l'età del veicolo in anni"""
        return date.today().year - self.anno_immatricolazione
    
    def prossime_scadenze(self, giorni=30):
        """Restituisce le scadenze entro i prossimi giorni specificati"""
        from datetime import timedelta
        scadenza_limite = date.today() + timedelta(days=giorni)
        
        scadenze = []
        
        # Controlla scadenze documenti
        documenti = self.documenti.filter(
            data_scadenza__lte=scadenza_limite,
            data_scadenza__gte=date.today()
        )
        for doc in documenti:
            scadenze.append({
                'tipo': 'documento',
                'nome': doc.tipo,
                'data': doc.data_scadenza,
                'giorni_rimanenti': (doc.data_scadenza - date.today()).days
            })
        
        # Controlla manutenzioni programmate
        manutenzioni = self.manutenzioni.filter(
            data_prevista__lte=scadenza_limite,
            data_prevista__gte=date.today(),
            completata=False
        )
        for man in manutenzioni:
            scadenze.append({
                'tipo': 'manutenzione',
                'nome': man.get_tipo_display(),
                'data': man.data_prevista,
                'giorni_rimanenti': (man.data_prevista - date.today()).days
            })
        
        return sorted(scadenze, key=lambda x: x['data'])


class DocumentoAutomezzo(models.Model):
    """Gestione dei documenti associati agli automezzi"""
    
    TIPO_DOCUMENTO_CHOICES = [
        ('assicurazione', 'Assicurazione'),
        ('revisione', 'Revisione'),
        ('bollo', 'Bollo'),
        ('libretto', 'Libretto di circolazione'),
        ('altro', 'Altro documento'),
    ]
    
    automezzo = models.ForeignKey(Automezzo, on_delete=models.CASCADE, related_name='documenti')
    tipo = models.CharField(max_length=20, choices=TIPO_DOCUMENTO_CHOICES)
    numero_documento = models.CharField(max_length=100, blank=True, null=True)
    data_rilascio = models.DateField()
    data_scadenza = models.DateField()
    costo = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    file_documento = models.FileField(upload_to='automezzi/documenti/', blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Documento Automezzo"
        verbose_name_plural = "Documenti Automezzi"
        ordering = ['-data_scadenza']
    
    def __str__(self):
        return f"{self.automezzo.targa} - {self.get_tipo_display()}"
    
    @property
    def giorni_alla_scadenza(self):
        """Calcola i giorni rimanenti alla scadenza"""
        if self.data_scadenza:
            delta = self.data_scadenza - date.today()
            return delta.days
        return None
    
    @property
    def is_scaduto(self):
        """Verifica se il documento è scaduto"""
        return self.data_scadenza < date.today()
    
    @property
    def is_in_scadenza(self):
        """Verifica se il documento scade entro 30 giorni"""
        giorni = self.giorni_alla_scadenza
        return giorni is not None and 0 <= giorni <= 30


class Manutenzione(models.Model):
    """Gestione delle manutenzioni degli automezzi"""
    
    TIPO_MANUTENZIONE_CHOICES = [
        ('ordinaria', 'Manutenzione Ordinaria'),
        ('straordinaria', 'Manutenzione Straordinaria'),
        ('tagliando', 'Tagliando'),
        ('riparazione', 'Riparazione'),
        ('gomme', 'Cambio Gomme'),
        ('altro', 'Altro'),
    ]
    
    automezzo = models.ForeignKey(Automezzo, on_delete=models.CASCADE, related_name='manutenzioni')
    tipo = models.CharField(max_length=20, choices=TIPO_MANUTENZIONE_CHOICES)
    descrizione = models.TextField()
    data_prevista = models.DateField()
    data_effettuata = models.DateField(blank=True, null=True)
    chilometri_manutenzione = models.PositiveIntegerField(blank=True, null=True)
    costo_previsto = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    costo_effettivo = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, blank=True, null=True)
    completata = models.BooleanField(default=False)
    responsabile = models.ForeignKey(
        'dipendenti.Dipendente',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='manutenzioni_responsabile'
    )
    note = models.TextField(blank=True, null=True)
    
    # File allegati (fatture, report, ecc.)
    file_allegato = models.FileField(upload_to='automezzi/manutenzioni/', blank=True, null=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Manutenzione"
        verbose_name_plural = "Manutenzioni"
        ordering = ['-data_prevista']
    
    def __str__(self):
        status = "✓" if self.completata else "⏳"
        return f"{status} {self.automezzo.targa} - {self.get_tipo_display()} ({self.data_prevista})"
    
    def save(self, *args, **kwargs):
        # Se la manutenzione viene marcata come completata, imposta la data effettuata
        if self.completata and not self.data_effettuata:
            self.data_effettuata = date.today()
        super().save(*args, **kwargs)


class RifornimentoCarburante(models.Model):
    """Gestione dei rifornimenti di carburante"""
    
    automezzo = models.ForeignKey(Automezzo, on_delete=models.CASCADE, related_name='rifornimenti')
    data_rifornimento = models.DateField(default=date.today)
    chilometri = models.PositiveIntegerField(help_text="Chilometraggio al momento del rifornimento")
    litri = models.DecimalField(max_digits=6, decimal_places=2, help_text="Litri riforniti")
    costo_totale = models.DecimalField(max_digits=8, decimal_places=2, help_text="Costo totale del rifornimento")
    costo_per_litro = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    distributore = models.CharField(max_length=200, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    
    # Chi ha effettuato il rifornimento
    effettuato_da = models.ForeignKey(
        'dipendenti.Dipendente',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rifornimenti_effettuati'
    )
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Rifornimento"
        verbose_name_plural = "Rifornimenti"
        ordering = ['-data_rifornimento']
    
    def __str__(self):
        return f"{self.automezzo.targa} - {self.data_rifornimento} ({self.litri}L)"
    
    def save(self, *args, **kwargs):
        # Calcola automaticamente il costo per litro se non specificato
        if not self.costo_per_litro and self.litri:
            self.costo_per_litro = self.costo_totale / self.litri
        
        # Aggiorna i chilometri dell'automezzo se necessario
        if self.chilometri > self.automezzo.chilometri_attuali:
            self.automezzo.chilometri_attuali = self.chilometri
            self.automezzo.save()
        
        super().save(*args, **kwargs)
    
    @property
    def chilometri_precedente(self):
        """Ottiene il chilometraggio del rifornimento precedente"""
        rifornimento_precedente = RifornimentoCarburante.objects.filter(
            automezzo=self.automezzo,
            data_rifornimento__lt=self.data_rifornimento
        ).order_by('-data_rifornimento').first()
        
        if rifornimento_precedente:
            return rifornimento_precedente.chilometri
        return self.automezzo.chilometri_iniziali
    
    @property
    def chilometri_percorsi(self):
        """Calcola i chilometri percorsi dall'ultimo rifornimento"""
        return self.chilometri - self.chilometri_precedente
    
    @property
    def consumo_per_100km(self):
        """Calcola il consumo per 100km dall'ultimo rifornimento"""
        if self.chilometri_percorsi > 0:
            return (self.litri / self.chilometri_percorsi) * 100
        return None


class EventoAutomezzo(models.Model):
    """Eventi generici associati agli automezzi (sinistri, verifiche, altro)"""
    
    TIPO_EVENTO_CHOICES = [
        ('sinistro', 'Sinistro'),
        ('furto', 'Furto/Tentato Furto'),
        ('multa', 'Multa'),
        ('verifica', 'Verifica/Controllo'),
        ('altro', 'Altro Evento'),
    ]
    
    automezzo = models.ForeignKey(Automezzo, on_delete=models.CASCADE, related_name='eventi')
    tipo = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES)
    data_evento = models.DateField(default=date.today)
    chilometri = models.PositiveIntegerField(blank=True, null=True)
    descrizione = models.TextField()
    costo = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    risolto = models.BooleanField(default=False)
    note = models.TextField(blank=True, null=True)
    
    # File allegati (foto, documenti, ecc.)
    file_allegato = models.FileField(upload_to='automezzi/eventi/', blank=True, null=True)
    
    # Riferimento al dipendente coinvolto
    dipendente_coinvolto = models.ForeignKey(
        'dipendenti.Dipendente',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventi_automezzi'
    )
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Evento Automezzo"
        verbose_name_plural = "Eventi Automezzi"
        ordering = ['-data_evento']
    
    def __str__(self):
        status = "✓" if self.risolto else "⚠️"
        return f"{status} {self.automezzo.targa} - {self.get_tipo_display()} ({self.data_evento})"


# Modello per statistiche rapide (opzionale, si può calcolare al volo)
class StatisticheAutomezzo(models.Model):
    """Statistiche calcolate per gli automezzi (aggiornate periodicamente)"""
    
    automezzo = models.OneToOneField(Automezzo, on_delete=models.CASCADE, related_name='statistiche')
    
    # Consumi
    consumo_medio = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="L/100km")
    costo_km_carburante = models.DecimalField(max_digits=8, decimal_places=4, default=0.0000, help_text="€/km")
    
    # Costi
    costo_manutenzioni_anno = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    costo_totale_km = models.DecimalField(max_digits=8, decimal_places=4, default=0.0000, help_text="€/km totale")
    
    # Date ultime operazioni
    ultimo_rifornimento = models.DateField(blank=True, null=True)
    ultima_manutenzione = models.DateField(blank=True, null=True)
    
    # Timestamp
    aggiornato_al = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Statistiche Automezzo"
        verbose_name_plural = "Statistiche Automezzi"
    
    def __str__(self):
        return f"Statistiche {self.automezzo.targa}"
    
    def aggiorna_statistiche(self):
        """Aggiorna le statistiche dell'automezzo"""
        # Calcola consumo medio
        rifornimenti = self.automezzo.rifornimenti.all().order_by('data_rifornimento')
        if rifornimenti.count() > 1:
            # Calcolo consumo medio su tutti i rifornimenti
            consumo_totale = sum([r.litri for r in rifornimenti])
            km_totali = self.automezzo.chilometri_totali
            if km_totali > 0:
                self.consumo_medio = (consumo_totale / km_totali) * 100
        
        # Calcola costo carburante per km
        if rifornimenti:
            costo_carburante_totale = sum([r.costo_totale for r in rifornimenti])
            if self.automezzo.chilometri_totali > 0:
                self.costo_km_carburante = costo_carburante_totale / self.automezzo.chilometri_totali
        
        # Calcola costi manutenzioni ultimo anno
        from datetime import timedelta
        anno_fa = date.today() - timedelta(days=365)
        manutenzioni_anno = self.automezzo.manutenzioni.filter(
            data_effettuata__gte=anno_fa,
            completata=True
        )
        self.costo_manutenzioni_anno = sum([m.costo_effettivo or 0 for m in manutenzioni_anno])
        
        # Date ultime operazioni
        ultimo_rif = rifornimenti.last()
        if ultimo_rif:
            self.ultimo_rifornimento = ultimo_rif.data_rifornimento
            
        ultima_man = self.automezzo.manutenzioni.filter(completata=True).first()
        if ultima_man:
            self.ultima_manutenzione = ultima_man.data_effettuata
        
        self.save()