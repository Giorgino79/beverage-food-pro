# anagrafica/models.py

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
import re

User = get_user_model()

class Rappresentante(models.Model):
    """Modello per i rappresentanti commerciali"""
    
    # Collegamento al modello Dipendente
    dipendente = models.OneToOneField(
        'dipendenti.Dipendente',
        on_delete=models.CASCADE,
        related_name='rappresentante'
    )
    
    # Dati anagrafici (se diversi dal dipendente)
    nome = models.CharField(max_length=100, blank=True)
    cognome = models.CharField(max_length=100, blank=True)
    indirizzo = models.TextField(blank=True)
    citta = models.CharField(max_length=100, blank=True)
    cap = models.CharField(max_length=10, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    # Dati fiscali
    partita_iva = models.CharField(max_length=15, blank=True)
    codice_fiscale = models.CharField(max_length=16, blank=True)
    
    # Dati commerciali
    percentuale_provvigione = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00,
        help_text="Percentuale di provvigione (0-100)"
    )
    zona_competenza = models.CharField(max_length=200, blank=True)
    
    # Stato
    attivo = models.BooleanField(default=True)
    note = models.TextField(blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Rappresentante"
        verbose_name_plural = "Rappresentanti"
        ordering = ['dipendente__last_name', 'dipendente__first_name']
    
    def __str__(self):
        nome_completo = f"{self.dipendente.first_name} {self.dipendente.last_name}".strip()
        return nome_completo or self.dipendente.username
    
    def get_absolute_url(self):
        return reverse('anagrafica:dettaglio_rappresentante', kwargs={'pk': self.pk})
    
    def clean(self):
        """Validazioni personalizzate"""
        # Validazione P.IVA
        if self.partita_iva:
            self.partita_iva = self.partita_iva.replace(' ', '').upper()
            if not self._validate_partita_iva(self.partita_iva):
                raise ValidationError({
                    'partita_iva': 'Partita IVA non valida'
                })
        
        # Validazione CF
        if self.codice_fiscale:
            self.codice_fiscale = self.codice_fiscale.replace(' ', '').upper()
            if not self._validate_codice_fiscale(self.codice_fiscale):
                raise ValidationError({
                    'codice_fiscale': 'Codice Fiscale non valido'
                })
    
    def _validate_partita_iva(self, piva):
        """Validazione Partita IVA italiana"""
        if not piva.startswith('IT'):
            return False
        numbers = piva[2:]
        if len(numbers) != 11 or not numbers.isdigit():
            return False
        
        # Calcolo checksum
        odd_chars = [int(numbers[i]) for i in range(0, 10, 2)]
        even_chars = [int(numbers[i]) for i in range(1, 10, 2)]
        
        total = sum(odd_chars)
        for char in even_chars:
            doubled = char * 2
            total += doubled // 10 + doubled % 10
        
        check_digit = (10 - (total % 10)) % 10
        return check_digit == int(numbers[10])
    
    def _validate_codice_fiscale(self, cf):
        """Validazione Codice Fiscale"""
        # Pattern per persone fisiche (16 caratteri)
        pattern_persona = r'^[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]$'
        # Pattern per aziende (11 cifre)
        pattern_azienda = r'^\d{11}$'
        
        return bool(re.match(pattern_persona, cf) or re.match(pattern_azienda, cf))


class Cliente(models.Model):
    """Modello per i clienti"""
    
    TIPO_PAGAMENTO_CHOICES = [
        ('immediato', 'Immediato'),
        ('15_giorni', '15 giorni'),
        ('30_giorni', '30 giorni'),
        ('60_giorni', '60 giorni'),
        ('90_giorni', '90 giorni'),
        ('bonifico', 'Bonifico bancario'),
        ('assegno', 'Assegno'),
    ]
    
    # Collegamento al rappresentante
    rappresentante = models.ForeignKey(
        Rappresentante,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clienti'
    )
    
    # Dati anagrafici
    nome = models.CharField(max_length=200, help_text="Nome o Ragione Sociale")
    indirizzo = models.TextField(blank=True)
    citta = models.CharField(max_length=100, blank=True)
    cap = models.CharField(max_length=10, blank=True)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    
    # Dati fiscali (almeno uno tra P.IVA e CF deve essere fornito)
    partita_iva = models.CharField(max_length=15, blank=True)
    codice_fiscale = models.CharField(max_length=16, blank=True)
    codice_univoco = models.CharField(max_length=10, blank=True)
    pec = models.EmailField(blank=True)
    
    # Dati commerciali
    tipo_pagamento = models.CharField(
        max_length=20,
        choices=TIPO_PAGAMENTO_CHOICES,
        default='immediato'
    )
    limite_credito = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    # Zona geografica
    zona = models.CharField(max_length=100, blank=True)
    
    # Stato
    attivo = models.BooleanField(default=True)
    note = models.TextField(blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clienti"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
    
    def get_absolute_url(self):
        return reverse('anagrafica:dettaglio_cliente', kwargs={'pk': self.pk})
    
    def clean(self):
        """Validazioni personalizzate"""
        # Almeno uno tra P.IVA e CF deve essere fornito
        if not self.partita_iva and not self.codice_fiscale:
            raise ValidationError({
                'partita_iva': 'Specificare almeno Partita IVA o Codice Fiscale',
                'codice_fiscale': 'Specificare almeno Partita IVA o Codice Fiscale'
            })
        
        # Validazione P.IVA
        if self.partita_iva:
            self.partita_iva = self.partita_iva.replace(' ', '').upper()
            if not self._validate_partita_iva(self.partita_iva):
                raise ValidationError({
                    'partita_iva': 'Partita IVA non valida'
                })
        
        # Validazione CF
        if self.codice_fiscale:
            self.codice_fiscale = self.codice_fiscale.replace(' ', '').upper()
            if not self._validate_codice_fiscale(self.codice_fiscale):
                raise ValidationError({
                    'codice_fiscale': 'Codice Fiscale non valido'
                })
    
    def _validate_partita_iva(self, piva):
        """Validazione Partita IVA italiana"""
        if not piva.startswith('IT'):
            return False
        numbers = piva[2:]
        if len(numbers) != 11 or not numbers.isdigit():
            return False
        
        # Calcolo checksum
        odd_chars = [int(numbers[i]) for i in range(0, 10, 2)]
        even_chars = [int(numbers[i]) for i in range(1, 10, 2)]
        
        total = sum(odd_chars)
        for char in even_chars:
            doubled = char * 2
            total += doubled // 10 + doubled % 10
        
        check_digit = (10 - (total % 10)) % 10
        return check_digit == int(numbers[10])
    
    def _validate_codice_fiscale(self, cf):
        """Validazione Codice Fiscale"""
        pattern_persona = r'^[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]$'
        pattern_azienda = r'^\d{11}$'
        return bool(re.match(pattern_persona, cf) or re.match(pattern_azienda, cf))


class Fornitore(models.Model):
    """Modello per i fornitori"""
    
    CATEGORIA_CHOICES = [
        ('materie_prime', 'Materie Prime'),
        ('semilavorati', 'Semilavorati'),
        ('servizi', 'Servizi'),
        ('consulenza', 'Consulenza'),
        ('software', 'Software/IT'),
        ('altri', 'Altri'),
    ]
    
    TIPO_PAGAMENTO_CHOICES = [
        ('immediato', 'Immediato'),
        ('15_giorni', '15 giorni'),
        ('30_giorni', '30 giorni'),
        ('60_giorni', '60 giorni'),
        ('90_giorni', '90 giorni'),
        ('bonifico', 'Bonifico bancario'),
    ]
    
    # Dati anagrafici
    nome = models.CharField(max_length=200, help_text="Nome o Ragione Sociale")
    indirizzo = models.TextField(blank=True)
    citta = models.CharField(max_length=100, blank=True)
    cap = models.CharField(max_length=10, blank=True)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    
    # Dati fiscali
    partita_iva = models.CharField(max_length=15)
    codice_fiscale = models.CharField(max_length=16, blank=True)
    
    # Dati bancari
    iban = models.CharField(max_length=34, blank=True)
    
    # Dati commerciali
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIA_CHOICES,
        default='altri'
    )
    tipo_pagamento = models.CharField(
        max_length=20,
        choices=TIPO_PAGAMENTO_CHOICES,
        default='30_giorni'
    )
    
    # Referente
    referente_nome = models.CharField(max_length=100, blank=True)
    referente_telefono = models.CharField(max_length=20, blank=True)
    referente_email = models.EmailField(blank=True)
    
    # Stato
    attivo = models.BooleanField(default=True)
    note = models.TextField(blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Fornitore"
        verbose_name_plural = "Fornitori"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
    
    def get_absolute_url(self):
        return reverse('anagrafica:dettaglio_fornitore', kwargs={'pk': self.pk})
    
    def clean(self):
        """Validazioni personalizzate"""
        # Validazione P.IVA
        if self.partita_iva:
            self.partita_iva = self.partita_iva.replace(' ', '').upper()
            if not self._validate_partita_iva(self.partita_iva):
                raise ValidationError({
                    'partita_iva': 'Partita IVA non valida'
                })
        
        # Validazione CF
        if self.codice_fiscale:
            self.codice_fiscale = self.codice_fiscale.replace(' ', '').upper()
            if not self._validate_codice_fiscale(self.codice_fiscale):
                raise ValidationError({
                    'codice_fiscale': 'Codice Fiscale non valido'
                })
        
        # Validazione IBAN
        if self.iban:
            self.iban = self.iban.replace(' ', '').upper()
            if not self._validate_iban(self.iban):
                raise ValidationError({
                    'iban': 'IBAN non valido'
                })
    
    def _validate_partita_iva(self, piva):
        """Validazione Partita IVA italiana"""
        if not piva.startswith('IT'):
            return False
        numbers = piva[2:]
        if len(numbers) != 11 or not numbers.isdigit():
            return False
        
        # Calcolo checksum
        odd_chars = [int(numbers[i]) for i in range(0, 10, 2)]
        even_chars = [int(numbers[i]) for i in range(1, 10, 2)]
        
        total = sum(odd_chars)
        for char in even_chars:
            doubled = char * 2
            total += doubled // 10 + doubled % 10
        
        check_digit = (10 - (total % 10)) % 10
        return check_digit == int(numbers[10])
    
    def _validate_codice_fiscale(self, cf):
        """Validazione Codice Fiscale"""
        pattern_persona = r'^[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]$'
        pattern_azienda = r'^\d{11}$'
        return bool(re.match(pattern_persona, cf) or re.match(pattern_azienda, cf))
    
    def _validate_iban(self, iban):
        """Validazione IBAN italiana base"""
        if not iban.startswith('IT'):
            return False
        if len(iban) != 27:  # IBAN italiano: IT + 25 caratteri
            return False
        return True