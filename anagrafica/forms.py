# anagrafica/forms.py

from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, Div, HTML
from crispy_forms.bootstrap import TabHolder, Tab
from .models import Rappresentante, Cliente, Fornitore
import re


class RappresentanteForm(forms.ModelForm):
    """Form per la gestione dei rappresentanti"""
    
    class Meta:
        model = Rappresentante
        fields = [
            'dipendente', 'nome', 'cognome', 'indirizzo', 'citta', 'cap',
            'telefono', 'email', 'partita_iva', 'codice_fiscale',
            'percentuale_provvigione', 'zona_competenza', 'attivo', 'note'
        ]
        widgets = {
            'indirizzo': forms.Textarea(attrs={'rows': 3}),
            'note': forms.Textarea(attrs={'rows': 3}),
            'percentuale_provvigione': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '100'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Migliora i widget
        self.fields['nome'].widget.attrs.update({'class': 'form-control'})
        self.fields['cognome'].widget.attrs.update({'class': 'form-control'})
        self.fields['telefono'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['partita_iva'].widget.attrs.update({'class': 'form-control', 'placeholder': 'IT12345678901'})
        self.fields['codice_fiscale'].widget.attrs.update({'class': 'form-control', 'placeholder': 'RSSMRA85M01H501Z'})
        self.fields['zona_competenza'].widget.attrs.update({'class': 'form-control'})
        
        # Labels personalizzate
        self.fields['dipendente'].label = 'Collegamento Dipendente'
        self.fields['percentuale_provvigione'].label = 'Percentuale Provvigione (%)'
        self.fields['zona_competenza'].label = 'Zona di Competenza'
    
    def clean_partita_iva(self):
        piva = self.cleaned_data.get('partita_iva', '')
        if piva:
            piva = piva.replace(' ', '').upper()
            if not self._validate_partita_iva(piva):
                raise ValidationError('Partita IVA non valida. Formato: IT + 11 cifre')
        return piva
    
    def clean_codice_fiscale(self):
        cf = self.cleaned_data.get('codice_fiscale', '')
        if cf:
            cf = cf.replace(' ', '').upper()
            if not self._validate_codice_fiscale(cf):
                raise ValidationError('Codice Fiscale non valido')
        return cf
    
    def clean_percentuale_provvigione(self):
        perc = self.cleaned_data.get('percentuale_provvigione')
        if perc is not None and (perc < 0 or perc > 100):
            raise ValidationError('La percentuale deve essere tra 0 e 100')
        return perc
    
    def _validate_partita_iva(self, piva):
        """Validazione Partita IVA italiana"""
        if not piva.startswith('IT'):
            return False
        numbers = piva[2:]
        if len(numbers) != 11 or not numbers.isdigit():
            return False
        
        # Calcolo checksum per P.IVA italiana
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


class ClienteForm(forms.ModelForm):
    """Form per la gestione dei clienti (SENZA sconto_percentuale)"""
    
    class Meta:
        model = Cliente
        fields = [
            'nome', 'rappresentante', 'zona', 'indirizzo', 'citta', 'cap',
            'telefono', 'email', 'partita_iva', 'codice_fiscale',
            'codice_univoco', 'pec', 'tipo_pagamento', 'limite_credito',
            'attivo', 'note'
        ]
        widgets = {
            'indirizzo': forms.Textarea(attrs={'rows': 3}),
            'note': forms.Textarea(attrs={'rows': 3}),
            'limite_credito': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Se l'utente è un rappresentante, nascondi il campo rappresentante e impostalo automaticamente
        if user and hasattr(user, 'rappresentante') and not user.is_staff:
            self.fields['rappresentante'].widget = forms.HiddenInput()
            self.fields['rappresentante'].initial = user.rappresentante
        
        # Migliora i widget e placeholder
        self.fields['nome'].widget.attrs.update({'class': 'form-control'})
        self.fields['telefono'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['partita_iva'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'IT12345678901'
        })
        self.fields['codice_fiscale'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'RSSMRA85M01H501Z'
        })
        self.fields['codice_univoco'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'XXXXXXX'
        })
        self.fields['pec'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'esempio@pec.it'
        })
        self.fields['zona'].widget.attrs.update({'class': 'form-control'})
        self.fields['citta'].widget.attrs.update({'class': 'form-control'})
        self.fields['cap'].widget.attrs.update({
            'class': 'form-control', 
            'maxlength': '5',
            'pattern': '[0-9]{5}'
        })
        
        # Labels personalizzate
        self.fields['nome'].label = 'Nome/Ragione Sociale *'
        self.fields['rappresentante'].label = 'Rappresentante'
        self.fields['telefono'].label = 'Telefono *'
        self.fields['email'].label = 'Email *'
        self.fields['partita_iva'].label = 'Partita IVA'
        self.fields['codice_fiscale'].label = 'Codice Fiscale'
        self.fields['codice_univoco'].label = 'Codice Univoco'
        self.fields['tipo_pagamento'].label = 'Tipo di Pagamento'
        self.fields['limite_credito'].label = 'Limite di Credito (€)'
        
        # Help text
        self.fields['partita_iva'].help_text = 'Formato: IT + 11 cifre'
        self.fields['codice_fiscale'].help_text = '16 caratteri per persone fisiche, 11 per aziende'
        self.fields['codice_univoco'].help_text = 'Per fatturazione elettronica'
        self.fields['limite_credito'].help_text = 'Limite massimo di credito concedibile'
    
    def clean(self):
        cleaned_data = super().clean()
        piva = cleaned_data.get('partita_iva')
        cf = cleaned_data.get('codice_fiscale')
        
        # Almeno uno tra P.IVA e CF deve essere fornito
        if not piva and not cf:
            raise ValidationError({
                'partita_iva': 'Specificare almeno Partita IVA o Codice Fiscale',
                'codice_fiscale': 'Specificare almeno Partita IVA o Codice Fiscale'
            })
        
        return cleaned_data
    
    def clean_partita_iva(self):
        piva = self.cleaned_data.get('partita_iva', '')
        if piva:
            piva = piva.replace(' ', '').upper()
            if not self._validate_partita_iva(piva):
                raise ValidationError('Partita IVA non valida. Formato: IT + 11 cifre')
        return piva
    
    def clean_codice_fiscale(self):
        cf = self.cleaned_data.get('codice_fiscale', '')
        if cf:
            cf = cf.replace(' ', '').upper()
            if not self._validate_codice_fiscale(cf):
                raise ValidationError('Codice Fiscale non valido')
        return cf
    
    def clean_limite_credito(self):
        limite = self.cleaned_data.get('limite_credito')
        if limite is not None and limite < 0:
            raise ValidationError('Il limite di credito non può essere negativo')
        return limite
    
    def _validate_partita_iva(self, piva):
        """Validazione Partita IVA italiana con checksum"""
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


class FornitoreForm(forms.ModelForm):
    """Form per la gestione dei fornitori"""
    
    class Meta:
        model = Fornitore
        fields = [
            'nome', 'indirizzo', 'citta', 'cap', 'telefono', 'email',
            'partita_iva', 'codice_fiscale', 'iban', 'categoria',
            'tipo_pagamento', 'referente_nome', 'referente_telefono',
            'referente_email', 'attivo', 'note'
        ]
        widgets = {
            'indirizzo': forms.Textarea(attrs={'rows': 3}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Migliora i widget
        self.fields['nome'].widget.attrs.update({'class': 'form-control'})
        self.fields['telefono'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['partita_iva'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'IT12345678901'
        })
        self.fields['codice_fiscale'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'RSSMRA85M01H501Z'
        })
        self.fields['iban'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'IT60X0542811101000000123456'
        })
        self.fields['citta'].widget.attrs.update({'class': 'form-control'})
        self.fields['cap'].widget.attrs.update({
            'class': 'form-control', 
            'maxlength': '5',
            'pattern': '[0-9]{5}'
        })
        self.fields['referente_nome'].widget.attrs.update({'class': 'form-control'})
        self.fields['referente_telefono'].widget.attrs.update({'class': 'form-control'})
        self.fields['referente_email'].widget.attrs.update({'class': 'form-control'})
        
        # Labels personalizzate
        self.fields['nome'].label = 'Nome/Ragione Sociale *'
        self.fields['telefono'].label = 'Telefono *'
        self.fields['email'].label = 'Email *'
        self.fields['partita_iva'].label = 'Partita IVA *'
        self.fields['codice_fiscale'].label = 'Codice Fiscale'
        self.fields['categoria'].label = 'Categoria Merceologica'
        self.fields['tipo_pagamento'].label = 'Tipo di Pagamento'
        self.fields['referente_nome'].label = 'Nome Referente'
        self.fields['referente_telefono'].label = 'Telefono Referente'
        self.fields['referente_email'].label = 'Email Referente'
        
        # Help text
        self.fields['partita_iva'].help_text = 'Formato: IT + 11 cifre'
        self.fields['iban'].help_text = 'IBAN per bonifici (IT + 25 caratteri)'
    
    def clean_partita_iva(self):
        piva = self.cleaned_data.get('partita_iva', '')
        if piva:
            piva = piva.replace(' ', '').upper()
            if not self._validate_partita_iva(piva):
                raise ValidationError('Partita IVA non valida. Formato: IT + 11 cifre')
        return piva
    
    def clean_codice_fiscale(self):
        cf = self.cleaned_data.get('codice_fiscale', '')
        if cf:
            cf = cf.replace(' ', '').upper()
            if not self._validate_codice_fiscale(cf):
                raise ValidationError('Codice Fiscale non valido')
        return cf
    
    def clean_iban(self):
        iban = self.cleaned_data.get('iban', '')
        if iban:
            iban = iban.replace(' ', '').upper()
            if not self._validate_iban(iban):
                raise ValidationError('IBAN non valido. Formato: IT + 25 caratteri')
        return iban
    
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
        """Validazione IBAN italiana semplificata"""
        if not iban.startswith('IT'):
            return False
        if len(iban) != 27:  # IBAN italiano: IT + 25 caratteri
            return False
        # Verifica che dopo IT ci siano numeri e lettere nel formato corretto
        code_part = iban[2:]
        if not re.match(r'^\d{2}[A-Z]\d{5}\d{10}[A-Z0-9]{12}$', code_part):
            return False
        return True


class AnagraficaSearchForm(forms.Form):
    """Form di ricerca nell'anagrafica"""
    
    TIPO_CHOICES = [
        ('', 'Tutti'),
        ('rappresentanti', 'Rappresentanti'),
        ('clienti', 'Clienti'),
        ('fornitori', 'Fornitori'),
    ]
    
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Cerca per nome, email, telefono...',
            'class': 'form-control'
        }),
        label='Cerca'
    )
    
    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tipo'
    )
    
    attivo = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Solo attivi'
    )