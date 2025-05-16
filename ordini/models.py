# ordini/models.py - Versione Completa e Migliorata
from django.db import models
from decimal import Decimal, InvalidOperation
from django.core.validators import MinValueValidator, RegexValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
import os
import uuid


# Upload paths
def upload_categoria_icon(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"categoria_{instance.pk}_{uuid.uuid4()}.{ext}"
    return os.path.join('categorie', 'icone', filename)


def upload_ordine_pdf(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"ordine_{instance.pk}_{uuid.uuid4()}.{ext}"
    return os.path.join('ordini', 'pdf', str(timezone.now().year), filename)


class Categoria(models.Model):
    """Categoria di prodotti"""
    nome_categoria = models.CharField(max_length=200, unique=True)
    descrizione = models.TextField(blank=True)
    icona = models.ImageField(upload_to=upload_categoria_icon, blank=True, null=True)
    attiva = models.BooleanField(default=True)
    ordinamento = models.PositiveIntegerField(default=0)
    creata_il = models.DateTimeField(auto_now_add=True)
    modificata_il = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorie"
        ordering = ['ordinamento', 'nome_categoria']

    def __str__(self):
        return self.nome_categoria


class Prodotto(models.Model):
    """Prodotto migliorato"""
    
    class Misura(models.TextChoices):
        BOTTIGLIA = 'bottiglia', 'Vendita a bottiglia'
        KILO = 'kilo', 'Vendita al peso (kg)'
        LITRO = 'litro', 'Vendita al litro'
        CONFEZIONE = 'confezione', 'Vendita a confezione'
        PEZZO = 'pezzo', 'Vendita a pezzo'
        CARTONE = 'cartone', 'Vendita a cartone'

    class AliquotaIva(models.TextChoices):
        QUATTRO = '4', 'IVA 4%'
        DIECI = '10', 'IVA 10%'
        VENTIDUE = '22', 'IVA 22%'

    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    nome_prodotto = models.CharField(max_length=200)
    descrizione = models.TextField(blank=True)
    
    # EAN MIGLIORATO - CharField invece di IntegerField
    ean = models.CharField(
        max_length=13,
        unique=True,
        validators=[RegexValidator(regex=r'^\d{13}$', message='EAN deve essere di 13 cifre')]
    )
    codice_interno = models.CharField(max_length=50, blank=True, unique=True)
    
    misura = models.CharField(max_length=15, choices=Misura.choices, default=Misura.CONFEZIONE)
    peso_netto = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    volume = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    
    aliquota_iva = models.CharField(max_length=3, choices=AliquotaIva.choices, default=AliquotaIva.VENTIDUE)
    
    # Gestione stock
    scorta_minima = models.PositiveIntegerField(default=0)
    scorta_massima = models.PositiveIntegerField(default=0)
    
    attivo = models.BooleanField(default=True)
    creato_il = models.DateTimeField(auto_now_add=True)
    modificato_il = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Prodotto"
        verbose_name_plural = "Prodotti"
        ordering = ['categoria', 'nome_prodotto']

    def __str__(self):
        return f"{self.nome_prodotto} ({self.ean})"

    def get_aliquota_iva_numerica(self):
        """Restituisce l'aliquota IVA come valore decimale"""
        try:
            return Decimal(self.aliquota_iva) / 100
        except:
            return Decimal('0.22')


class Ordine(models.Model):
    """Ordine migliorato con stati"""
    
    class StatusOrdine(models.TextChoices):
        BOZZA = 'bozza', 'Bozza'
        INVIATO = 'inviato', 'Inviato al Fornitore'
        CONFERMATO = 'confermato', 'Confermato dal Fornitore'
        IN_PRODUZIONE = 'in_produzione', 'In Produzione'
        SPEDITO = 'spedito', 'Spedito'
        IN_TRANSITO = 'in_transito', 'In Transito'
        RICEVUTO = 'ricevuto', 'Ricevuto'
        COMPLETATO = 'completato', 'Completato'
        ANNULLATO = 'annullato', 'Annullato'

    class Misura(models.TextChoices):
        BOTTIGLIA = 'bottiglia', 'Vendita a bottiglia'
        KILO = 'kilo', 'Vendita al peso'
        LITRO = 'litro', 'Vendita al litro'
        CONFEZIONE = 'confezione', 'Vendita a confezione'
        PEZZO = 'pezzo', 'Vendita a pezzo'
        CARTONE = 'cartone', 'Vendita a cartone'

    # Relazioni
    prodotto = models.ForeignKey(Prodotto, on_delete=models.PROTECT)
    fornitore = models.ForeignKey('anagrafica.Fornitore', on_delete=models.PROTECT)
    
    # Numero ordine automatico
    numero_ordine = models.CharField(max_length=20, unique=True, blank=True)
    
    # Quantità e misura
    misura = models.CharField(max_length=50, choices=Misura.choices, default=Misura.CONFEZIONE)
    pezzi_per_confezione = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    quantita_ordinata = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    
    # Prezzi
    prezzo_unitario_ordine = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    sconto_percentuale = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))]
    )
    prezzo_totale_ordine = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    totale_ordine_ivato = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    
    # Stato e date
    status = models.CharField(max_length=20, choices=StatusOrdine.choices, default=StatusOrdine.BOZZA)
    data_creazione_ordine = models.DateTimeField(auto_now_add=True)
    data_invio_ordine = models.DateField(null=True, blank=True)
    data_arrivo_previsto = models.DateField(null=True, blank=True)
    data_ricezione_ordine = models.DateField(null=True, blank=True)
    
    # File e email
    pdf_ordine = models.FileField(upload_to=upload_ordine_pdf, blank=True, null=True)
    email_inviata = models.BooleanField(default=False)
    data_invio_email = models.DateTimeField(null=True, blank=True)
    
    # Note
    note_interne = models.TextField(blank=True)
    note_fornitore = models.TextField(blank=True)
    
    # Audit
    creato_da = models.ForeignKey('dipendenti.Dipendente', on_delete=models.SET_NULL, null=True, blank=True)
    modificato_il = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ordine"
        verbose_name_plural = "Ordini"
        ordering = ['-data_creazione_ordine']
        constraints = [
            models.CheckConstraint(check=models.Q(quantita_ordinata__gt=0), name='ordine_quantita_positiva'),
            models.CheckConstraint(check=models.Q(prezzo_unitario_ordine__gt=0), name='ordine_prezzo_positivo'),
        ]

    def __str__(self):
        return f"Ordine {self.numero_ordine or self.id} - {self.prodotto.nome_prodotto}"

    def save(self, *args, **kwargs):
        # Genera numero ordine auto
        if not self.numero_ordine:
            anno = timezone.now().year
            count = Ordine.objects.filter(numero_ordine__startswith=f"ORD{anno}").count()
            self.numero_ordine = f"ORD{anno}{count + 1:04d}"

        # Copia misura dal prodotto se non specificata
        if not self.misura and self.prodotto:
            self.misura = self.prodotto.misura

        # Calcola prezzi
        if self.prodotto and self.quantita_ordinata and self.prezzo_unitario_ordine:
            # Applica sconto
            prezzo_scontato = self.prezzo_unitario_ordine * (1 - self.sconto_percentuale / 100)
            
            # Calcola totale
            if self.misura == self.Misura.CONFEZIONE and self.pezzi_per_confezione:
                self.prezzo_totale_ordine = prezzo_scontato * self.pezzi_per_confezione * self.quantita_ordinata
            else:
                self.prezzo_totale_ordine = prezzo_scontato * self.quantita_ordinata
            
            # Calcola IVA
            aliquota_iva = self.prodotto.get_aliquota_iva_numerica()
            self.totale_ordine_ivato = self.prezzo_totale_ordine * (Decimal('1.0') + aliquota_iva)

        # Auto-update status
        if self.data_ricezione_ordine and self.status not in [self.StatusOrdine.COMPLETATO, self.StatusOrdine.ANNULLATO]:
            self.status = self.StatusOrdine.RICEVUTO
        elif self.data_invio_ordine and self.status == self.StatusOrdine.BOZZA:
            self.status = self.StatusOrdine.INVIATO

        super().save(*args, **kwargs)

    def is_in_ritardo(self):
        """Verifica se l'ordine è in ritardo"""
        if self.data_arrivo_previsto and not self.data_ricezione_ordine:
            return date.today() > self.data_arrivo_previsto
        return False


class Ricezione(models.Model):
    """Ricezione ordine"""
    ordine = models.OneToOneField(Ordine, on_delete=models.CASCADE, related_name='ricezione')
    data_ricezione = models.DateField(default=date.today)
    ricevuto_da = models.ForeignKey('dipendenti.Dipendente', on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(blank=True)
    creata_il = models.DateTimeField(auto_now_add=True)
    modificata_il = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ricezione"
        verbose_name_plural = "Ricezioni"
        ordering = ['-data_ricezione']

    def __str__(self):
        return f"Ricezione Ordine {self.ordine.numero_ordine or self.ordine.id}"


class ProdottoRicevuto(models.Model):
    """Dettaglio prodotti ricevuti"""
    ricezione = models.ForeignKey(Ricezione, on_delete=models.CASCADE, related_name='prodotti_ricevuti')
    prodotto = models.ForeignKey(Prodotto, on_delete=models.PROTECT)
    quantita_ricevuta = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    data_scadenza = models.DateField(null=True, blank=True)
    numero_lotto = models.CharField(max_length=50, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        verbose_name = "Prodotto Ricevuto"
        verbose_name_plural = "Prodotti Ricevuti"
        constraints = [
            models.CheckConstraint(check=models.Q(quantita_ricevuta__gt=0), name='prodotto_ricevuto_quantita_positiva'),
        ]

    def __str__(self):
        return f"{self.prodotto.nome_prodotto} (Ric. {self.ricezione.ordine.numero_ordine})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Aggiorna magazzino automaticamente
        self.aggiorna_magazzino()

    def aggiorna_magazzino(self):
        """Aggiorna il magazzino con la quantità ricevuta"""
        magazzino_entry, created = Magazzino.objects.get_or_create(
            prodotto=self.prodotto,
            data_scadenza=self.data_scadenza,
            numero_lotto=self.numero_lotto,
            defaults={
                'quantita_in_magazzino': 0,
                'data_ingresso': self.ricezione.data_ricezione
            }
        )
        
        if not created:
            magazzino_entry.quantita_in_magazzino += self.quantita_ricevuta
            magazzino_entry.save()


class Magazzino(models.Model):
    """Inventario magazzino con FIFO"""
    prodotto = models.ForeignKey(Prodotto, on_delete=models.CASCADE)
    quantita_in_magazzino = models.PositiveIntegerField(default=0)
    data_scadenza = models.DateField(null=True, blank=True)
    numero_lotto = models.CharField(max_length=50, blank=True)
    data_ingresso = models.DateField(default=date.today)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Posizione in magazzino
    settore = models.CharField(max_length=10, blank=True)
    scaffale = models.CharField(max_length=10, blank=True)
    piano = models.CharField(max_length=10, blank=True)
    
    creato_il = models.DateTimeField(auto_now_add=True)
    modificato_il = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Magazzino"
        verbose_name_plural = "Magazzino"
        ordering = ['prodotto__nome_prodotto', 'data_scadenza']
        unique_together = [['prodotto', 'data_scadenza', 'numero_lotto']]
        constraints = [
            models.CheckConstraint(check=models.Q(quantita_in_magazzino__gte=0), name='magazzino_quantita_non_negativa'),
        ]

    def __str__(self):
        scadenza = self.data_scadenza.strftime('%d/%m/%Y') if self.data_scadenza else 'N/A'
        return f"{self.prodotto.nome_prodotto} - Scad: {scadenza} - Qta: {self.quantita_in_magazzino}"

    def giorni_alla_scadenza(self):
        """Calcola i giorni rimanenti alla scadenza"""
        if self.data_scadenza:
            return (self.data_scadenza - date.today()).days
        return None

    def is_scaduto(self):
        """Verifica se il prodotto è scaduto"""
        if self.data_scadenza:
            return self.data_scadenza < date.today()
        return False

    def is_in_scadenza(self, giorni=30):
        """Verifica se il prodotto scade entro N giorni"""
        if self.data_scadenza:
            return self.giorni_alla_scadenza() <= giorni
        return False


# Manager custom per query ottimizzate
class OrdineManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('prodotto', 'fornitore', 'prodotto__categoria')
    
    def bozze(self):
        return self.filter(status=Ordine.StatusOrdine.BOZZA)
    
    def inviati(self):
        return self.filter(status=Ordine.StatusOrdine.INVIATO)
    
    def da_ricevere(self):
        return self.filter(status__in=[
            Ordine.StatusOrdine.INVIATO,
            Ordine.StatusOrdine.CONFERMATO,
            Ordine.StatusOrdine.IN_PRODUZIONE,
            Ordine.StatusOrdine.SPEDITO,
            Ordine.StatusOrdine.IN_TRANSITO
        ])
    
    def ricevuti(self):
        return self.filter(status=Ordine.StatusOrdine.RICEVUTO)
    
    def in_ritardo(self):
        return self.filter(
            data_arrivo_previsto__lt=date.today(),
            status__in=[
                Ordine.StatusOrdine.INVIATO,
                Ordine.StatusOrdine.CONFERMATO,
                Ordine.StatusOrdine.IN_PRODUZIONE,
                Ordine.StatusOrdine.SPEDITO,
                Ordine.StatusOrdine.IN_TRANSITO
            ]
        )


class MagazzinoManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('prodotto', 'prodotto__categoria')
    
    def disponibili(self):
        return self.filter(quantita_in_magazzino__gt=0)
    
    def scorte_basse(self):
        return self.filter(
            quantita_in_magazzino__lte=models.F('prodotto__scorta_minima'),
            quantita_in_magazzino__gt=0
        )
    
    def in_scadenza(self, giorni=30):
        data_limite = date.today() + timedelta(days=giorni)
        return self.filter(
            data_scadenza__lte=data_limite,
            data_scadenza__gte=date.today(),
            quantita_in_magazzino__gt=0
        )


# Aggiungi i manager ai modelli
Ordine.add_to_class('objects', OrdineManager())
Magazzino.add_to_class('objects', MagazzinoManager())


# Signal handlers
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Ordine)
def log_ordine_changes(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Nuovo ordine creato: {instance.numero_ordine} - {instance.prodotto.nome_prodotto}")
    else:
        logger.info(f"Ordine modificato: {instance.numero_ordine} - Status: {instance.status}")

@receiver(post_save, sender=Ricezione)
def aggiorna_ordine_su_ricezione(sender, instance, created, **kwargs):
    if created:
        ordine = instance.ordine
        if not ordine.data_ricezione_ordine:
            ordine.data_ricezione_ordine = instance.data_ricezione
            ordine.status = Ordine.StatusOrdine.RICEVUTO
            ordine.save(update_fields=['data_ricezione_ordine', 'status'])