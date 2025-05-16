# Implementazione App Anagrafica - Backup Completo
    
## Data generazione: 2025-05-13 03:46:54


## 1. Models.py

```python
from django.db import models
from django.urls import reverse
from django.core.validators import MinLengthValidator, MaxLengthValidator, EmailValidator
from django.core.exceptions import ValidationError
import re


class Rappresentante(models.Model):
    """
    Modello per i rappresentanti commerciali che gestiscono clienti
    """
    user = models.ForeignKey(
        'dipendenti.Dipendente', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Utente associato al rappresentante"
    )
    nome = models.CharField(max_length=200, verbose_name="Nome completo")
    ragione_sociale = models.CharField(max_length=200, verbose_name="Ragione sociale")
    indirizzo = models.CharField(max_length=200, verbose_name="Indirizzo")
    cap = models.CharField(
        max_length=5, 
        verbose_name="CAP",
        validators=[MinLengthValidator(5), MaxLengthValidator(5)]
    )
    città = models.CharField(max_length=200, verbose_name="Città")
    provincia = models.CharField(
        max_length=2, 
        verbose_name="Provincia",
        validators=[MinLengthValidator(2), MaxLengthValidator(2)]
    )
    partita_iva = models.CharField(
        max_length=11, 
        verbose_name="Partita IVA",
        validators=[MinLengthValidator(11), MaxLengthValidator(11)]
    )
    codice_fiscale = models.CharField(
        max_length=16, 
        verbose_name="Codice fiscale",
        validators=[MinLengthValidator(16), MaxLengthValidator(16)]
    )
    codice_univoco = models.CharField(
        max_length=7, 
        verbose_name="Codice univoco",
        help_text="Codice destinatario fatturazione elettronica"
    )
    telefono = models.CharField(max_length=50, verbose_name="Telefono")
    email = models.EmailField(verbose_name="Email", validators=[EmailValidator()])
    zona = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Zona di competenza"
    )
    percentuale_sulle_vendite = models.FloatField(
        verbose_name="Percentuale sulle vendite (%)",
        help_text="Percentuale di provvigione sulle vendite"
    )
    
    # Campi aggiuntivi
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_modifica = models.DateTimeField(auto_now=True)
    attivo = models.BooleanField(default=True, verbose_name="Attivo")
    note = models.TextField(blank=True, null=True, verbose_name="Note")
    
    class Meta:
        verbose_name = "Rappresentante"
        verbose_name_plural = "Rappresentanti"
        ordering = ['nome']
    
    def clean(self):
        """Validazioni personalizzate"""
        super().clean()
        
        # Validazione codice fiscale
        if self.codice_fiscale:
            if not self._is_valid_codice_fiscale(self.codice_fiscale):
                raise ValidationError({'codice_fiscale': 'Codice fiscale non valido'})
        
        # Validazione partita IVA
        if self.partita_iva:
            if not self._is_valid_partita_iva(self.partita_iva):
                raise ValidationError({'partita_iva': 'Partita IVA non valida'})
    
    def _is_valid_codice_fiscale(self, cf):
        """Validazione semplice del codice fiscale"""
        if len(cf) != 16:
            return False
        
        # Pattern per codice fiscale persona fisica
        pattern = r'^[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]$'
        if re.match(pattern, cf.upper()):
            return True
        
        # Pattern per codice fiscale persona giuridica
        pattern_pg = r'^\d{11}$'
        return bool(re.match(pattern_pg, cf))
    
    def _is_valid_partita_iva(self, piva):
        """Validazione semplice della partita IVA"""
        return len(piva) == 11 and piva.isdigit()
    
    def get_absolute_url(self):
        return reverse("anagrafica:vedirappresentante", kwargs={"pk": self.pk})
    
    def __str__(self):
        return f'{self.nome} - {self.zona or "Senza zona"}'


class Cliente(models.Model):
    """
    Modello per i clienti dell'azienda
    """
    class Pagatipo(models.TextChoices):
        IMMEDIATO = '01', 'Immediato'
        TRENTA = '30', '30 gg df'
        SESSANTA = '60', '60 gg df'
        NOVANTA = '90', '90 gg df'
    
    rappresentante = models.ForeignKey(
        Rappresentante, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='clienti',
        verbose_name="Rappresentante"
    )
    zona = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Zona"
    )
    ragione_sociale = models.CharField(max_length=200, verbose_name="Ragione sociale")
    indirizzo = models.CharField(max_length=200, verbose_name="Indirizzo")
    cap = models.CharField(
        max_length=5, 
        verbose_name="CAP",
        validators=[MinLengthValidator(5), MaxLengthValidator(5)]
    )
    città = models.CharField(max_length=200, verbose_name="Città")
    provincia = models.CharField(
        max_length=2, 
        verbose_name="Provincia",
        validators=[MinLengthValidator(2), MaxLengthValidator(2)]
    )
    partita_iva = models.CharField(
        max_length=11, 
        verbose_name="Partita IVA",
        validators=[MinLengthValidator(11), MaxLengthValidator(11)],
        blank=True,
        null=True
    )
    codice_fiscale = models.CharField(
        max_length=16, 
        verbose_name="Codice fiscale",
        validators=[MinLengthValidator(11)]  # Minimo 11 per partita IVA
    )
    codice_univoco = models.CharField(
        max_length=7, 
        verbose_name="Codice univoco",
        help_text="Codice destinatario fatturazione elettronica"
    )
    telefono = models.CharField(max_length=50, verbose_name="Telefono")
    email = models.EmailField(verbose_name="Email", validators=[EmailValidator()])
    pagamento = models.CharField(
        max_length=20, 
        choices=Pagatipo.choices, 
        default='01',
        verbose_name="Tipo di pagamento"
    )
    
    # Campi aggiuntivi per gestione cliente
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_modifica = models.DateTimeField(auto_now=True)
    attivo = models.BooleanField(default=True, verbose_name="Cliente attivo")
    
    # Campi opzionali per informazioni commerciali
    limite_credito = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Limite di credito (€)"
    )
    sconto_percentuale = models.FloatField(
        default=0.0,
        verbose_name="Sconto percentuale",
        help_text="Sconto predefinito per questo cliente"
    )
    note = models.TextField(blank=True, null=True, verbose_name="Note")
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clienti"
        ordering = ['ragione_sociale']
        unique_together = ['partita_iva', 'codice_fiscale']
    
    def clean(self):
        """Validazioni personalizzate"""
        super().clean()
        
        # Validazione codice fiscale
        if self.codice_fiscale:
            if not self._is_valid_codice_fiscale(self.codice_fiscale):
                raise ValidationError({'codice_fiscale': 'Codice fiscale non valido'})
        
        # Validazione partita IVA
        if self.partita_iva:
            if not self._is_valid_partita_iva(self.partita_iva):
                raise ValidationError({'partita_iva': 'Partita IVA non valida'})
        
        # Almeno uno tra partita IVA e codice fiscale deve essere inserito
        if not self.partita_iva and not self.codice_fiscale:
            raise ValidationError('Inserire almeno uno tra Partita IVA e Codice Fiscale')
    
    def _is_valid_codice_fiscale(self, cf):
        """Validazione semplice del codice fiscale"""
        if len(cf) not in [11, 16]:  # Partita IVA o codice fiscale
            return False
        
        if len(cf) == 11:
            return cf.isdigit()
        
        # Pattern per codice fiscale persona fisica
        pattern = r'^[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]$'
        return bool(re.match(pattern, cf.upper()))
    
    def _is_valid_partita_iva(self, piva):
        """Validazione semplice della partita IVA"""
        return len(piva) == 11 and piva.isdigit()
    
    def get_absolute_url(self):
        return reverse("anagrafica:vedicliente", kwargs={"pk": self.pk})
    
    def __str__(self):
        if self.rappresentante:
            return f'{self.ragione_sociale} - {self.rappresentante.nome}'
        return f'{self.ragione_sociale}'


class Fornitore(models.Model):
    """
    Modello per i fornitori dell'azienda
    """
    class Pagatipo(models.TextChoices):
        IMMEDIATO = '01', 'Immediato'
        TRENTA = '30', '30 gg df'
        SESSANTA = '60', '60 gg df'
        NOVANTA = '90', '90 gg df'
    
    ragione_sociale = models.CharField(max_length=200, verbose_name="Ragione sociale")
    indirizzo = models.CharField(max_length=200, verbose_name="Indirizzo")
    cap = models.CharField(
        max_length=5, 
        verbose_name="CAP",
        validators=[MinLengthValidator(5), MaxLengthValidator(5)]
    )
    città = models.CharField(max_length=200, verbose_name="Città")
    provincia = models.CharField(
        max_length=2, 
        verbose_name="Provincia",
        validators=[MinLengthValidator(2), MaxLengthValidator(2)]
    )
    partita_iva = models.CharField(
        max_length=11, 
        verbose_name="Partita IVA",
        validators=[MinLengthValidator(11), MaxLengthValidator(11)],
        blank=True,
        null=True
    )
    codice_fiscale = models.CharField(
        max_length=16, 
        verbose_name="Codice fiscale",
        validators=[MinLengthValidator(11)]  # Minimo 11 per partita IVA
    )
    codice_univoco = models.CharField(
        max_length=7, 
        verbose_name="Codice univoco",
        help_text="Codice destinatario fatturazione elettronica",
        blank=True,
        null=True
    )
    telefono = models.CharField(max_length=50, verbose_name="Telefono")
    email = models.EmailField(verbose_name="Email", validators=[EmailValidator()])
    pagamento = models.CharField(
        max_length=20, 
        choices=Pagatipo.choices, 
        default='30',
        verbose_name="Tipo di pagamento"
    )
    
    # Campi aggiuntivi per gestione fornitore
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_modifica = models.DateTimeField(auto_now=True)
    attivo = models.BooleanField(default=True, verbose_name="Fornitore attivo")
    
    # Campi specifici per fornitori
    categoria = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Categoria merceologica",
        help_text="Es: Materiali elettrici, Ricambi auto, ecc."
    )
    iban = models.CharField(
        max_length=34, 
        blank=True, 
        null=True,
        verbose_name="IBAN",
        help_text="Codice IBAN per i pagamenti"
    )
    referente = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name="Referente principale"
    )
    note = models.TextField(blank=True, null=True, verbose_name="Note")
    
    class Meta:
        verbose_name = "Fornitore"
        verbose_name_plural = "Fornitori"
        ordering = ['ragione_sociale']
        unique_together = ['partita_iva', 'codice_fiscale']
    
    def clean(self):
        """Validazioni personalizzate"""
        super().clean()
        
        # Validazione codice fiscale
        if self.codice_fiscale:
            if not self._is_valid_codice_fiscale(self.codice_fiscale):
                raise ValidationError({'codice_fiscale': 'Codice fiscale non valido'})
        
        # Validazione partita IVA
        if self.partita_iva:
            if not self._is_valid_partita_iva(self.partita_iva):
                raise ValidationError({'partita_iva': 'Partita IVA non valida'})
        
        # Almeno uno tra partita IVA e codice fiscale deve essere inserito
        if not self.partita_iva and not self.codice_fiscale:
            raise ValidationError('Inserire almeno uno tra Partita IVA e Codice Fiscale')
        
        # Validazione IBAN (se presente)
        if self.iban:
            if not self._is_valid_iban(self.iban):
                raise ValidationError({'iban': 'IBAN non valido'})
    
    def _is_valid_codice_fiscale(self, cf):
        """Validazione semplice del codice fiscale"""
        if len(cf) not in [11, 16]:  # Partita IVA o codice fiscale
            return False
        
        if len(cf) == 11:
            return cf.isdigit()
        
        # Pattern per codice fiscale persona fisica
        pattern = r'^[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]$'
        return bool(re.match(pattern, cf.upper()))
    
    def _is_valid_partita_iva(self, piva):
        """Validazione semplice della partita IVA"""
        return len(piva) == 11 and piva.isdigit()
    
    def _is_valid_iban(self, iban):
        """Validazione semplice dell'IBAN"""
        # Rimuove spazi e converte in maiuscolo
        iban = iban.replace(' ', '').upper()
        
        # Verifica lunghezza (22 caratteri per IT)
        if not iban.startswith('IT') or len(iban) != 27:
            return False
        
        # Verifica che dopo IT ci siano 2 cifre di controllo
        if not iban[2:4].isdigit():
            return False
        
        # Verifica che il resto siano caratteri alfanumerici
        return iban[4:].isalnum()
    
    def get_absolute_url(self):
        return reverse("anagrafica:vedifornitore", kwargs={"pk": self.pk})
    
    def __str__(self):
        return f'{self.ragione_sociale}'
```


## 2. Forms.py

```python
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, HTML, Div
from crispy_forms.bootstrap import TabHolder, Tab, FormActions
from .models import Rappresentante, Cliente, Fornitore
import re
from django.db import models  # Aggiunto questo import

class RappresentanteForm(forms.ModelForm):
    """Form per la gestione dei rappresentanti"""
    
    class Meta:
        model = Rappresentante
        fields = [
            'user', 'nome', 'ragione_sociale', 'indirizzo', 'cap', 'città', 
            'provincia', 'partita_iva', 'codice_fiscale', 'codice_univoco',
            'telefono', 'email', 'zona', 'percentuale_sulle_vendite', 
            'attivo', 'note'
        ]
        widgets = {
            'partita_iva': forms.TextInput(attrs={
                'placeholder': '12345678901',
                'pattern': '[0-9]{11}',
                'title': 'Inserire 11 cifre numeriche'
            }),
            'codice_fiscale': forms.TextInput(attrs={
                'placeholder': 'RSSMRA85M01H501Z',
                'maxlength': 16,
                'title': '16 caratteri per persona fisica, 11 per azienda'
            }),
            'cap': forms.TextInput(attrs={
                'placeholder': '00000',
                'pattern': '[0-9]{5}',
                'title': 'Codice Avviamento Postale (5 cifre)'
            }),
            'provincia': forms.TextInput(attrs={
                'placeholder': 'MI',
                'maxlength': 2,
                'style': 'text-transform: uppercase;'
            }),
            'codice_univoco': forms.TextInput(attrs={
                'placeholder': '0000000',
                'maxlength': 7,
                'title': 'Codice destinatario fatturazione elettronica'
            }),
            'percentuale_sulle_vendite': forms.NumberInput(attrs={
                'min': 0,
                'max': 100,
                'step': 0.01,
                'placeholder': '0.00'
            }),
            'note': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Note aggiuntive...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtriamo solo i dipendenti con livello rappresentante o staff
        from dipendenti.models import Dipendente
        self.fields['user'].queryset = Dipendente.objects.filter(
            models.Q(livello=Dipendente.Autorizzazioni.rappresentante) |
            models.Q(is_staff=True)
        ).order_by('first_name', 'last_name')
        
        # Configurazione crispy forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        self.helper.layout = Layout(
            TabHolder(
                Tab('Informazioni Generali',
                    Div(
                        'user',
                        'nome',
                        'ragione_sociale',
                        css_class='tab-pane'
                    ),
                    Fieldset('Indirizzo',
                        Row(
                            Column('indirizzo', css_class='col-md-8'),
                            Column('cap', css_class='col-md-2'),
                            Column('provincia', css_class='col-md-2'),
                        ),
                        'città',
                        'zona',
                    ),
                ),
                Tab('Dati Fiscali',
                    HTML('<div class="alert alert-info mb-3">Inserire i dati fiscali del rappresentante</div>'),
                    'partita_iva',
                    'codice_fiscale',
                    'codice_univoco',
                ),
                Tab('Contatti e Condizioni',
                    'telefono',
                    'email',
                    'percentuale_sulle_vendite',
                    'attivo',
                    'note',
                ),
            ),
            FormActions(
                Submit('submit', 'Salva Rappresentante', css_class='btn btn-primary'),
                HTML('<a href="{% url "anagrafica:elenco_rappresentanti" %}" class="btn btn-secondary">Annulla</a>'),
            )
        )
    
    def clean_partita_iva(self):
        """Validazione partita IVA"""
        partita_iva = self.cleaned_data.get('partita_iva')
        if partita_iva:
            partita_iva = partita_iva.strip().replace(' ', '')
            if len(partita_iva) != 11 or not partita_iva.isdigit():
                raise ValidationError(_("La partita IVA deve essere di 11 cifre numeriche"))
            # Controllo checksum
            if not self._validate_partita_iva_checksum(partita_iva):
                raise ValidationError(_("La partita IVA non è valida (errore checksum)"))
        return partita_iva
    
    def clean_codice_fiscale(self):
        """Validazione codice fiscale"""
        codice_fiscale = self.cleaned_data.get('codice_fiscale')
        if codice_fiscale:
            codice_fiscale = codice_fiscale.upper().strip().replace(' ', '')
            if len(codice_fiscale) not in [11, 16]:
                raise ValidationError(_("Il codice fiscale deve essere di 11 o 16 caratteri"))
            
            if len(codice_fiscale) == 16:
                # Codice fiscale persona fisica
                pattern = r'^[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]$'
                if not re.match(pattern, codice_fiscale):
                    raise ValidationError(_("Formato codice fiscale non valido"))
            else:
                # Codice fiscale persona giuridica (stesso formato P.IVA)
                if not codice_fiscale.isdigit():
                    raise ValidationError(_("Codice fiscale persona giuridica non valido"))
        return codice_fiscale
    
    def clean_provincia(self):
        """Validazione provincia"""
        provincia = self.cleaned_data.get('provincia')
        if provincia:
            provincia = provincia.upper().strip()
            if len(provincia) != 2 or not provincia.isalpha():
                raise ValidationError(_("La provincia deve essere di 2 lettere (es: MI, RM)"))
        return provincia
    
    def _validate_partita_iva_checksum(self, piva):
        """Validazione checksum partita IVA italiana"""
        if len(piva) != 11:
            return False
        
        total = 0
        for i, digit in enumerate(piva[:-1]):
            value = int(digit)
            if i % 2 == 0:
                value *= 2
                if value > 9:
                    value = (value // 10) + (value % 10)
            total += value
        
        check_digit = (10 - (total % 10)) % 10
        return int(piva[-1]) == check_digit


class ClienteForm(forms.ModelForm):
    """Form per la gestione dei clienti"""
    
    class Meta:
        model = Cliente
        fields = [
            'rappresentante', 'zona', 'ragione_sociale', 'indirizzo', 'cap', 
            'città', 'provincia', 'partita_iva', 'codice_fiscale', 
            'codice_univoco', 'telefono', 'email', 'pagamento', 
            'limite_credito', 'sconto_percentuale', 'attivo', 'note'
        ]
        widgets = {
            'partita_iva': forms.TextInput(attrs={
                'placeholder': '12345678901 (opzionale)',
                'pattern': '[0-9]{11}',
                'title': 'Inserire 11 cifre numeriche se presente'
            }),
            'codice_fiscale': forms.TextInput(attrs={
                'placeholder': 'Codice fiscale o Partita IVA',
                'title': '16 caratteri per persona fisica, 11 per azienda'
            }),
            'cap': forms.TextInput(attrs={
                'placeholder': '00000',
                'pattern': '[0-9]{5}',
                'title': 'Codice Avviamento Postale (5 cifre)'
            }),
            'provincia': forms.TextInput(attrs={
                'placeholder': 'MI',
                'maxlength': 2,
                'style': 'text-transform: uppercase;'
            }),
            'codice_univoco': forms.TextInput(attrs={
                'placeholder': '0000000',
                'maxlength': 7,
                'title': 'Codice destinatario fatturazione elettronica'
            }),
            'limite_credito': forms.NumberInput(attrs={
                'min': 0,
                'step': 0.01,
                'placeholder': '0.00'
            }),
            'sconto_percentuale': forms.NumberInput(attrs={
                'min': 0,
                'max': 100,
                'step': 0.01,
                'placeholder': '0.00'
            }),
            'note': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Note aggiuntive...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Ordina i rappresentanti
        self.fields['rappresentante'].queryset = Rappresentante.objects.filter(
            attivo=True
        ).order_by('nome')
        
        # Configurazione crispy forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        self.helper.layout = Layout(
            TabHolder(
                Tab('Informazioni Generali',
                    'rappresentante',
                    'zona',
                    'ragione_sociale',
                    Fieldset('Indirizzo',
                        Row(
                            Column('indirizzo', css_class='col-md-8'),
                            Column('cap', css_class='col-md-2'),
                            Column('provincia', css_class='col-md-2'),
                        ),
                        'città',
                    ),
                ),
                Tab('Dati Fiscali',
                    HTML('<div class="alert alert-warning mb-3">'
                         '<i class="fas fa-exclamation-triangle"></i> '
                         'Inserire almeno uno tra Partita IVA e Codice Fiscale</div>'),
                    'partita_iva',
                    'codice_fiscale',
                    'codice_univoco',
                ),
                Tab('Contatti e Condizioni Commerciali',
                    Row(
                        Column('telefono', css_class='col-md-6'),
                        Column('email', css_class='col-md-6'),
                    ),
                    'pagamento',
                    Row(
                        Column('limite_credito', css_class='col-md-6'),
                        Column('sconto_percentuale', css_class='col-md-6'),
                    ),
                    'attivo',
                    'note',
                ),
            ),
            FormActions(
                Submit('submit', 'Salva Cliente', css_class='btn btn-primary'),
                HTML('<a href="{% url "anagrafica:elenco_clienti" %}" class="btn btn-secondary">Annulla</a>'),
            )
        )
    
    def clean(self):
        """Validazione personalizzata"""
        cleaned_data = super().clean()
        partita_iva = cleaned_data.get('partita_iva')
        codice_fiscale = cleaned_data.get('codice_fiscale')
        
        # Almeno uno tra partita IVA e codice fiscale deve essere presente
        if not partita_iva and not codice_fiscale:
            raise ValidationError(_('Inserire almeno uno tra Partita IVA e Codice Fiscale'))
        
        # Se entrambi sono presenti, devono essere diversi
        if partita_iva and codice_fiscale and partita_iva == codice_fiscale:
            # È lecito se è un'azienda (P.IVA = CF)
            if len(codice_fiscale) != 11 or not codice_fiscale.isdigit():
                raise ValidationError(_('Per le persone fisiche, Partita IVA e Codice Fiscale devono essere diversi'))
        
        return cleaned_data
    
    def clean_partita_iva(self):
        """Validazione partita IVA (opzionale per clienti)"""
        partita_iva = self.cleaned_data.get('partita_iva')
        if partita_iva:
            partita_iva = partita_iva.strip().replace(' ', '')
            if len(partita_iva) != 11 or not partita_iva.isdigit():
                raise ValidationError(_("La partita IVA deve essere di 11 cifre numeriche"))
        return partita_iva
    
    def clean_codice_fiscale(self):
        """Validazione codice fiscale"""
        codice_fiscale = self.cleaned_data.get('codice_fiscale')
        if codice_fiscale:
            codice_fiscale = codice_fiscale.upper().strip().replace(' ', '')
            if len(codice_fiscale) not in [11, 16]:
                raise ValidationError(_("Il codice fiscale deve essere di 11 o 16 caratteri"))
            
            if len(codice_fiscale) == 16:
                # Codice fiscale persona fisica
                pattern = r'^[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]$'
                if not re.match(pattern, codice_fiscale):
                    raise ValidationError(_("Formato codice fiscale non valido"))
        return codice_fiscale
    
    def clean_provincia(self):
        """Validazione provincia"""
        provincia = self.cleaned_data.get('provincia')
        if provincia:
            provincia = provincia.upper().strip()
            if len(provincia) != 2 or not provincia.isalpha():
                raise ValidationError(_("La provincia deve essere di 2 lettere (es: MI, RM)"))
        return provincia


class FornitoreForm(forms.ModelForm):
    """Form per la gestione dei fornitori"""
    
    class Meta:
        model = Fornitore
        fields = [
            'ragione_sociale', 'indirizzo', 'cap', 'città', 'provincia', 
            'partita_iva', 'codice_fiscale', 'codice_univoco', 'telefono', 
            'email', 'pagamento', 'categoria', 'iban', 'referente', 
            'attivo', 'note'
        ]
        widgets = {
            'partita_iva': forms.TextInput(attrs={
                'placeholder': '12345678901 (opzionale)',
                'pattern': '[0-9]{11}',
                'title': 'Inserire 11 cifre numeriche se presente'
            }),
            'codice_fiscale': forms.TextInput(attrs={
                'placeholder': 'Codice fiscale o Partita IVA',
                'title': '16 caratteri per persona fisica, 11 per azienda'
            }),
            'cap': forms.TextInput(attrs={
                'placeholder': '00000',
                'pattern': '[0-9]{5}',
                'title': 'Codice Avviamento Postale (5 cifre)'
            }),
            'provincia': forms.TextInput(attrs={
                'placeholder': 'MI',
                'maxlength': 2,
                'style': 'text-transform: uppercase;'
            }),
            'codice_univoco': forms.TextInput(attrs={
                'placeholder': '0000000 (opzionale)',
                'maxlength': 7,
                'title': 'Codice destinatario fatturazione elettronica'
            }),
            'iban': forms.TextInput(attrs={
                'placeholder': 'IT60 X054 2811 1010 0000 0123 456',
                'pattern': '[A-Z]{2}[0-9]{2}[A-Za-z0-9]{4}[0-9]{7}([A-Za-z0-9]?){0,16}',
                'title': 'Codice IBAN per i pagamenti'
            }),
            'categoria': forms.TextInput(attrs={
                'placeholder': 'es: Materiali elettrici, Ricambi auto...',
                'title': 'Categoria merceologica del fornitore'
            }),
            'referente': forms.TextInput(attrs={
                'placeholder': 'Nome del referente principale',
            }),
            'note': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Note aggiuntive...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurazione crispy forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        self.helper.layout = Layout(
            TabHolder(
                Tab('Informazioni Generali',
                    'ragione_sociale',
                    'categoria',
                    Fieldset('Indirizzo',
                        Row(
                            Column('indirizzo', css_class='col-md-8'),
                            Column('cap', css_class='col-md-2'),
                            Column('provincia', css_class='col-md-2'),
                        ),
                        'città',
                    ),
                ),
                Tab('Dati Fiscali',
                    HTML('<div class="alert alert-warning mb-3">'
                         '<i class="fas fa-exclamation-triangle"></i> '
                         'Inserire almeno uno tra Partita IVA e Codice Fiscale</div>'),
                    'partita_iva',
                    'codice_fiscale',
                    'codice_univoco',
                ),
                Tab('Contatti e Condizioni',
                    Row(
                        Column('telefono', css_class='col-md-6'),
                        Column('email', css_class='col-md-6'),
                    ),
                    'referente',
                    'pagamento',
                    'iban',
                    'attivo',
                    'note',
                ),
            ),
            FormActions(
                Submit('submit', 'Salva Fornitore', css_class='btn btn-primary'),
                HTML('<a href="{% url "anagrafica:elenco_fornitori" %}" class="btn btn-secondary">Annulla</a>'),
            )
        )
    
    def clean(self):
        """Validazione personalizzata"""
        cleaned_data = super().clean()
        partita_iva = cleaned_data.get('partita_iva')
        codice_fiscale = cleaned_data.get('codice_fiscale')
        
        # Almeno uno tra partita IVA e codice fiscale deve essere presente
        if not partita_iva and not codice_fiscale:
            raise ValidationError(_('Inserire almeno uno tra Partita IVA e Codice Fiscale'))
        
        return cleaned_data
    
    def clean_partita_iva(self):
        """Validazione partita IVA (opzionale per fornitori)"""
        partita_iva = self.cleaned_data.get('partita_iva')
        if partita_iva:
            partita_iva = partita_iva.strip().replace(' ', '')
            if len(partita_iva) != 11 or not partita_iva.isdigit():
                raise ValidationError(_("La partita IVA deve essere di 11 cifre numeriche"))
        return partita_iva
    
    def clean_codice_fiscale(self):
        """Validazione codice fiscale"""
        codice_fiscale = self.cleaned_data.get('codice_fiscale')
        if codice_fiscale:
            codice_fiscale = codice_fiscale.upper().strip().replace(' ', '')
            if len(codice_fiscale) not in [11, 16]:
                raise ValidationError(_("Il codice fiscale deve essere di 11 o 16 caratteri"))
            
            if len(codice_fiscale) == 16:
                # Codice fiscale persona fisica
                pattern = r'^[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]$'
                if not re.match(pattern, codice_fiscale):
                    raise ValidationError(_("Formato codice fiscale non valido"))
        return codice_fiscale
    
    def clean_provincia(self):
        """Validazione provincia"""
        provincia = self.cleaned_data.get('provincia')
        if provincia:
            provincia = provincia.upper().strip()
            if len(provincia) != 2 or not provincia.isalpha():
                raise ValidationError(_("La provincia deve essere di 2 lettere (es: MI, RM)"))
        return provincia
    
    def clean_iban(self):
        """Validazione IBAN"""
        iban = self.cleaned_data.get('iban')
        if iban:
            iban = iban.upper().replace(' ', '')
            
            # Verifica formato IBAN italiano
            if not iban.startswith('IT') or len(iban) != 27:
                raise ValidationError(_("L'IBAN deve iniziare con IT e avere 27 caratteri"))
            
            # Verifica che le prime 4 posizioni dopo IT siano numeriche
            if not iban[2:4].isdigit():
                raise ValidationError(_("Le cifre di controllo dell'IBAN non sono valide"))
            
            # Verifica che il resto sia alfanumerico
            if not iban[4:].isalnum():
                raise ValidationError(_("L'IBAN contiene caratteri non validi"))
            
            # Qui si potrebbe aggiungere la validazione mod-97
            return iban
        return None


# Form di ricerca per le anagrafiche
class AnagraficaSearchForm(forms.Form):
    """Form per la ricerca nelle anagrafiche"""
    
    TIPO_CHOICES = [
        ('', 'Tutti'),
        ('rappresentante', 'Rappresentanti'),
        ('cliente', 'Clienti'),
        ('fornitore', 'Fornitori'),
    ]
    
    search = forms.CharField(
        label='Cerca',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Cerca per nome, ragione sociale, email...',
            'class': 'form-control'
        })
    )
    
    tipo = forms.ChoiceField(
        label='Tipo',
        choices=TIPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    attivo = forms.BooleanField(
        label='Solo attivi',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurazione crispy forms
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Row(
                Column('search', css_class='col-md-6'),
                Column('tipo', css_class='col-md-3'),
                Column('attivo', css_class='col-md-1'),
                Column(
                    Submit('submit', 'Cerca', css_class='btn btn-primary'),
                    css_class='col-md-2'
                ),
            )
        )
```


## 3. Views.py

```python
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q, Count, Sum
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from dipendenti.models import Dipendente
from .models import Rappresentante, Cliente, Fornitore
from .forms import RappresentanteForm, ClienteForm, FornitoreForm, AnagraficaSearchForm


# Mixins personalizzati per i permessi
class StaffOrSuperuserRequiredMixin(UserPassesTestMixin):
    """Mixin per verificare che l'utente sia staff o superuser"""
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class RappresentanteAccessMixin(UserPassesTestMixin):
    """Mixin per verificare l'accesso ai rappresentanti"""
    def test_func(self):
        user = self.request.user
        # Staff, superuser o rappresentanti possono accedere
        return (user.is_staff or user.is_superuser or 
                user.livello == Dipendente.Autorizzazioni.rappresentante)


# Dashboard dell'anagrafica
@login_required
def dashboard_anagrafica(request):
    """Vista dashboard dell'anagrafica con statistiche principali"""
    context = {
        'page_title': 'Dashboard Anagrafica',
        'rappresentanti_count': Rappresentante.objects.filter(attivo=True).count(),
        'clienti_count': Cliente.objects.filter(attivo=True).count(),
        'fornitori_count': Fornitore.objects.filter(attivo=True).count(),
        'rappresentanti_senza_clienti': Rappresentante.objects.filter(
            clienti__isnull=True, attivo=True
        ).count(),
        'recent_rappresentanti': Rappresentante.objects.filter(attivo=True).order_by('-data_creazione')[:5],
        'recent_clienti': Cliente.objects.filter(attivo=True).order_by('-data_creazione')[:5],
        'recent_fornitori': Fornitore.objects.filter(attivo=True).order_by('-data_creazione')[:5],
    }
    return render(request, 'anagrafica/dashboard.html', context)


# ===================== RAPPRESENTANTI =====================

class RappresentanteListView(LoginRequiredMixin, StaffOrSuperuserRequiredMixin, ListView):
    """Vista lista rappresentanti con ricerca e filtri"""
    model = Rappresentante
    template_name = 'anagrafica/rappresentanti/elenco.html'
    context_object_name = 'rappresentanti'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Rappresentante.objects.all().order_by('nome')
        
        # Filtro ricerca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) |
                Q(ragione_sociale__icontains=search) |
                Q(email__icontains=search) |
                Q(telefono__icontains=search) |
                Q(zona__icontains=search)
            )
        
        # Filtro attivo
        if self.request.GET.get('attivo') == 'False':
            queryset = queryset.filter(attivo=False)
        else:
            queryset = queryset.filter(attivo=True)
        
        return queryset.annotate(clienti_count=Count('clienti'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = AnagraficaSearchForm(self.request.GET)
        context['total_count'] = self.get_queryset().count()
        return context


class RappresentanteDetailView(LoginRequiredMixin, RappresentanteAccessMixin, DetailView):
    """Vista dettaglio rappresentante"""
    model = Rappresentante
    template_name = 'anagrafica/rappresentanti/dettaglio.html'
    context_object_name = 'rappresentante'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Clienti del rappresentante
        context['clienti'] = self.object.clienti.filter(attivo=True)
        context['clienti_count'] = context['clienti'].count()
        # Statistiche vendite (se disponibili)
        # context['vendite_totali'] = self.object.vendite.aggregate(Sum('importo'))['importo__sum'] or 0
        return context


class RappresentanteCreateView(LoginRequiredMixin, StaffOrSuperuserRequiredMixin, CreateView):
    """Vista creazione nuovo rappresentante"""
    model = Rappresentante
    form_class = RappresentanteForm
    template_name = 'anagrafica/rappresentanti/nuovo.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Rappresentante "{}" creato con successo!').format(self.object.nome))
        return response
    
    def get_success_url(self):
        return reverse_lazy('anagrafica:dettaglio_rappresentante', kwargs={'pk': self.object.pk})


class RappresentanteUpdateView(LoginRequiredMixin, StaffOrSuperuserRequiredMixin, UpdateView):
    """Vista modifica rappresentante"""
    model = Rappresentante
    form_class = RappresentanteForm
    template_name = 'anagrafica/rappresentanti/modifica.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Rappresentante "{}" aggiornato con successo!').format(self.object.nome))
        return response
    
    def get_success_url(self):
        return reverse_lazy('anagrafica:dettaglio_rappresentante', kwargs={'pk': self.object.pk})


class RappresentanteDeleteView(LoginRequiredMixin, StaffOrSuperuserRequiredMixin, DeleteView):
    """Vista eliminazione rappresentante"""
    model = Rappresentante
    template_name = 'anagrafica/rappresentanti/elimina.html'
    success_url = reverse_lazy('anagrafica:elenco_rappresentanti')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Verifica se ha clienti associati
        if self.object.clienti.exists():
            messages.error(request, _('Impossibile eliminare il rappresentante. Ha clienti associati.'))
            return redirect('anagrafica:dettaglio_rappresentante', pk=self.object.pk)
        
        nome = self.object.nome
        response = super().delete(request, *args, **kwargs)
        messages.success(request, _('Rappresentante "{}" eliminato con successo!').format(nome))
        return response


# ===================== CLIENTI =====================

class ClienteListView(LoginRequiredMixin, ListView):
    """Vista lista clienti con ricerca e filtri"""
    model = Cliente
    template_name = 'anagrafica/clienti/elenco.html'
    context_object_name = 'clienti'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Cliente.objects.select_related('rappresentante').order_by('ragione_sociale')
        
        # Filtro per rappresentante (se l'utente è un rappresentante)
        user = self.request.user
        if (hasattr(user, 'livello') and 
            user.livello == Dipendente.Autorizzazioni.rappresentante and 
            not user.is_staff):
            # Trova il rappresentante associato all'utente
            try:
                rappresentante = Rappresentante.objects.get(user=user)
                queryset = queryset.filter(rappresentante=rappresentante)
            except Rappresentante.DoesNotExist:
                queryset = queryset.none()
        
        # Filtro ricerca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(ragione_sociale__icontains=search) |
                Q(codice_fiscale__icontains=search) |
                Q(partita_iva__icontains=search) |
                Q(email__icontains=search) |
                Q(telefone__icontains=search) |
                Q(città__icontains=search) |
                Q(rappresentante__nome__icontains=search)
            )
        
        # Filtro rappresentante
        rappresentante_id = self.request.GET.get('rappresentante')
        if rappresentante_id:
            queryset = queryset.filter(rappresentante_id=rappresentante_id)
        
        # Filtro attivo
        if self.request.GET.get('attivo') == 'False':
            queryset = queryset.filter(attivo=False)
        else:
            queryset = queryset.filter(attivo=True)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = AnagraficaSearchForm(self.request.GET)
        context['rappresentanti'] = Rappresentante.objects.filter(attivo=True).order_by('nome')
        context['total_count'] = self.get_queryset().count()
        return context


class ClienteDetailView(LoginRequiredMixin, DetailView):
    """Vista dettaglio cliente"""
    model = Cliente
    template_name = 'anagrafica/clienti/dettaglio.html'
    context_object_name = 'cliente'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        
        # Se l'utente è un rappresentante, verifica che possa vedere questo cliente
        user = self.request.user
        if (hasattr(user, 'livello') and 
            user.livello == Dipendente.Autorizzazioni.rappresentante and 
            not user.is_staff):
            try:
                rappresentante = Rappresentante.objects.get(user=user)
                if obj.rappresentante != rappresentante:
                    from django.http import Http404
                    raise Http404("Non hai i permessi per visualizzare questo cliente")
            except Rappresentante.DoesNotExist:
                from django.http import Http404
                raise Http404("Rappresentante non trovato")
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Qui si potrebbero aggiungere ordini, fatture, ecc.
        # context['ordini'] = self.object.ordini.all()[:5]
        # context['fatture'] = self.object.fatture.all()[:5]
        return context


class ClienteCreateView(LoginRequiredMixin, CreateView):
    """Vista creazione nuovo cliente"""
    model = Cliente
    form_class = ClienteForm
    template_name = 'anagrafica/clienti/nuovo.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        # Se l'utente è un rappresentante, preseleziona se stesso
        user = self.request.user
        if (hasattr(user, 'livello') and 
            user.livello == Dipendente.Autorizzazioni.rappresentante):
            try:
                rappresentante = Rappresentante.objects.get(user=user)
                form.fields['rappresentante'].initial = rappresentante
                # Se non è staff, blocca la modifica del rappresentante
                if not user.is_staff:
                    form.fields['rappresentante'].widget.attrs['readonly'] = True
            except Rappresentante.DoesNotExist:
                pass
        
        return form
    
    def form_valid(self, form):
        # Se l'utente è un rappresentante e non è staff, forza il rappresentante
        user = self.request.user
        if (hasattr(user, 'livello') and 
            user.livello == Dipendente.Autorizzazioni.rappresentante and 
            not user.is_staff):
            try:
                rappresentante = Rappresentante.objects.get(user=user)
                form.instance.rappresentante = rappresentante
            except Rappresentante.DoesNotExist:
                pass
        
        response = super().form_valid(form)
        messages.success(self.request, _('Cliente "{}" creato con successo!').format(self.object.ragione_sociale))
        return response
    
    def get_success_url(self):
        return reverse_lazy('anagrafica:dettaglio_cliente', kwargs={'pk': self.object.pk})


class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    """Vista modifica cliente"""
    model = Cliente
    form_class = ClienteForm
    template_name = 'anagrafica/clienti/modifica.html'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        
        # Se l'utente è un rappresentante, verifica che possa modificare questo cliente
        user = self.request.user
        if (hasattr(user, 'livello') and 
            user.livello == Dipendente.Autorizzazioni.rappresentante and 
            not user.is_staff):
            try:
                rappresentante = Rappresentante.objects.get(user=user)
                if obj.rappresentante != rappresentante:
                    from django.http import Http404
                    raise Http404("Non hai i permessi per modificare questo cliente")
            except Rappresentante.DoesNotExist:
                from django.http import Http404
                raise Http404("Rappresentante non trovato")
        
        return obj
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Cliente "{}" aggiornato con successo!').format(self.object.ragione_sociale))
        return response
    
    def get_success_url(self):
        return reverse_lazy('anagrafica:dettaglio_cliente', kwargs={'pk': self.object.pk})


class ClienteDeleteView(LoginRequiredMixin, StaffOrSuperuserRequiredMixin, DeleteView):
    """Vista eliminazione cliente"""
    model = Cliente
    template_name = 'anagrafica/clienti/elimina.html'
    success_url = reverse_lazy('anagrafica:elenco_clienti')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Verifica se ha ordini o fatture associate (quando implementate)
        # if self.object.ordini.exists() or self.object.fatture.exists():
        #     messages.error(request, _('Impossibile eliminare il cliente. Ha ordini o fatture associati.'))
        #     return redirect('anagrafica:dettaglio_cliente', pk=self.object.pk)
        
        ragione_sociale = self.object.ragione_sociale
        response = super().delete(request, *args, **kwargs)
        messages.success(request, _('Cliente "{}" eliminato con successo!').format(ragione_sociale))
        return response


# ===================== FORNITORI =====================

class FornitoreListView(LoginRequiredMixin, ListView):
    """Vista lista fornitori con ricerca e filtri"""
    model = Fornitore
    template_name = 'anagrafica/fornitori/elenco.html'
    context_object_name = 'fornitori'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Fornitore.objects.all().order_by('ragione_sociale')
        
        # Filtro ricerca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(ragione_sociale__icontains=search) |
                Q(codice_fiscale__icontains=search) |
                Q(partita_iva__icontains=search) |
                Q(email__icontains=search) |
                Q(telefono__icontains=search) |
                Q(città__icontains=search) |
                Q(categoria__icontains=search)
            )
        
        # Filtro categoria
        categoria = self.request.GET.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria__icontains=categoria)
        
        # Filtro attivo
        if self.request.GET.get('attivo') == 'False':
            queryset = queryset.filter(attivo=False)
        else:
            queryset = queryset.filter(attivo=True)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = AnagraficaSearchForm(self.request.GET)
        context['categorie'] = Fornitore.objects.values_list('categoria', flat=True).distinct().exclude(categoria__isnull=True)
        context['total_count'] = self.get_queryset().count()
        return context


class FornitoreDetailView(LoginRequiredMixin, DetailView):
    """Vista dettaglio fornitore"""
    model = Fornitore
    template_name = 'anagrafica/fornitori/dettaglio.html'
    context_object_name = 'fornitore'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Qui si potrebbero aggiungere ordini di acquisto, fatture, ecc.
        # context['ordini_acquisto'] = self.object.ordini_acquisto.all()[:5]
        # context['fatture_acquisto'] = self.object.fatture_acquisto.all()[:5]
        return context


class FornitoreCreateView(LoginRequiredMixin, StaffOrSuperuserRequiredMixin, CreateView):
    """Vista creazione nuovo fornitore"""
    model = Fornitore
    form_class = FornitoreForm
    template_name = 'anagrafica/fornitori/nuovo.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Fornitore "{}" creato con successo!').format(self.object.ragione_sociale))
        return response
    
    def get_success_url(self):
        return reverse_lazy('anagrafica:dettaglio_fornitore', kwargs={'pk': self.object.pk})


class FornitoreUpdateView(LoginRequiredMixin, StaffOrSuperuserRequiredMixin, UpdateView):
    """Vista modifica fornitore"""
    model = Fornitore
    form_class = FornitoreForm
    template_name = 'anagrafica/fornitori/modifica.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Fornitore "{}" aggiornato con successo!').format(self.object.ragione_sociale))
        return response
    
    def get_success_url(self):
        return reverse_lazy('anagrafica:dettaglio_fornitore', kwargs={'pk': self.object.pk})


class FornitoreDeleteView(LoginRequiredMixin, StaffOrSuperuserRequiredMixin, DeleteView):
    """Vista eliminazione fornitore"""
    model = Fornitore
    template_name = 'anagrafica/fornitori/elimina.html'
    success_url = reverse_lazy('anagrafica:elenco_fornitori')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Verifica se ha ordini di acquisto o fatture associate (quando implementate)
        # if self.object.ordini_acquisto.exists() or self.object.fatture_acquisto.exists():
        #     messages.error(request, _('Impossibile eliminare il fornitore. Ha ordini o fatture associati.'))
        #     return redirect('anagrafica:dettaglio_fornitore', pk=self.object.pk)
        
        ragione_sociale = self.object.ragione_sociale
        response = super().delete(request, *args, **kwargs)
        messages.success(request, _('Fornitore "{}" eliminato con successo!').format(ragione_sociale))
        return response


# ===================== API E RICERCHE =====================

@login_required
def api_search_anagrafica(request):
    """API per la ricerca rapida nell'anagrafica"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    results = []
    
    # Cerca nei rappresentanti
    rappresentanti = Rappresentante.objects.filter(
        Q(nome__icontains=query) |
        Q(ragione_sociale__icontains=query) |
        Q(telefono__icontains=query),
        attivo=True
    )[:5]
    
    for r in rappresentanti:
        results.append({
            'id': f'repr_{r.id}',
            'type': 'Rappresentante',
            'title': r.nome,
            'subtitle': r.ragione_sociale,
            'url': r.get_absolute_url(),
            'icon': 'fas fa-user-tie'
        })
    
    # Cerca nei clienti
    clienti = Cliente.objects.filter(
        Q(ragione_sociale__icontains=query) |
        Q(codice_fiscale__icontains=query) |
        Q(partita_iva__icontains=query) |
        Q(telefono__icontains=query),
        attivo=True
    )[:5]
    
    for c in clienti:
        results.append({
            'id': f'clie_{c.id}',
            'type': 'Cliente',
            'title': c.ragione_sociale,
            'subtitle': f'{c.città} - {c.rappresentante.nome if c.rappresentante else "Nessun rappresentante"}',
            'url': c.get_absolute_url(),
            'icon': 'fas fa-building'
        })
    
    # Cerca nei fornitori
    fornitori = Fornitore.objects.filter(
        Q(ragione_sociale__icontains=query) |
        Q(codice_fiscale__icontains=query) |
        Q(partita_iva__icontains=query) |
        Q(telefono__icontains=query),
        attivo=True
    )[:5]
    
    for f in fornitori:
        results.append({
            'id': f'forn_{f.id}',
            'type': 'Fornitore',
            'title': f.ragione_sociale,
            'subtitle': f'{f.città} - {f.categoria or "Non specificata"}',
            'url': f.get_absolute_url(),
            'icon': 'fas fa-truck'
        })
    
    return JsonResponse({'results': results})


@login_required
def export_anagrafica(request):
    """Esporta l'anagrafica in formato CSV/Excel"""
    import csv
    from django.http import HttpResponse
    
    format_type = request.GET.get('format', 'csv')
    tipo = request.GET.get('tipo', 'tutti')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="anagrafica_{tipo}.csv"'
    
    writer = csv.writer(response)
    
    if tipo == 'rappresentanti' or tipo == 'tutti':
        # Header rappresentanti
        writer.writerow(['Tipo', 'Nome', 'Ragione Sociale', 'Email', 'Telefono', 'Città', 'Provincia'])
        
        for r in Rappresentante.objects.filter(attivo=True):
            writer.writerow([
                'Rappresentante', r.nome, r.ragione_sociale, r.email, 
                r.telefono, r.città, r.provincia
            ])
    
    if tipo == 'clienti' or tipo == 'tutti':
        # Header clienti (se non già scritto)
        if tipo == 'clienti':
            writer.writerow(['Tipo', 'Ragione Sociale', 'Email', 'Telefono', 'Città', 'Rappresentante'])
        
        for c in Cliente.objects.filter(attivo=True).select_related('rappresentante'):
            writer.writerow([
                'Cliente', c.ragione_sociale, c.email, c.telefono, 
                c.città, c.rappresentante.nome if c.rappresentante else ''
            ])
    
    if tipo == 'fornitori' or tipo == 'tutti':
        # Header fornitori (se non già scritto)
        if tipo == 'fornitori':
            writer.writerow(['Tipo', 'Ragione Sociale', 'Email', 'Telefono', 'Città', 'Categoria'])
        
        for f in Fornitore.objects.filter(attivo=True):
            writer.writerow([
                'Fornitore', f.ragione_sociale, f.email, f.telefono, 
                f.città, f.categoria or ''
            ])
    
    return response


# Vista per toggle attivo/inattivo
@login_required
def toggle_attivo(request, tipo, pk):
    """Toggle dello stato attivo per rappresentanti, clienti, fornitori"""
    if not request.user.is_staff:
        messages.error(request, _('Non hai i permessi per questa operazione'))
        return redirect('anagrafica:dashboard')
    
    model_map = {
        'rappresentante': Rappresentante,
        'cliente': Cliente,
        'fornitore': Fornitore,
    }
    
    if tipo not in model_map:
        messages.error(request, _('Tipo non valido'))
        return redirect('anagrafica:dashboard')
    
    try:
        obj = model_map[tipo].objects.get(pk=pk)
        obj.attivo = not obj.attivo
        obj.save()
        
        stato = 'attivato' if obj.attivo else 'disattivato'
        messages.success(request, _(f'{tipo.capitalize()} "{obj}" {stato} con successo!'))
        
    except model_map[tipo].DoesNotExist:
        messages.error(request, _(f'{tipo.capitalize()} non trovato'))
    
    # Redirect alla pagina appropriata
    url_map = {
        'rappresentante': 'anagrafica:elenco_rappresentanti',
        'cliente': 'anagrafica:elenco_clienti',
        'fornitore': 'anagrafica:elenco_fornitori',
    }
    
    return redirect(url_map[tipo])
```


## 4. URLs.py

```python
from django.urls import path, include
from . import views
from . import views_extra  # Aggiungiamo l'import per views_extra

app_name = 'anagrafica'

# Pattern URL per l'app anagrafica
urlpatterns = [
    # Dashboard
    path('', views.dashboard_anagrafica, name='dashboard'),
    
    # ========== RAPPRESENTANTI ==========
    path('rappresentanti/', include([
        path('', views.RappresentanteListView.as_view(), name='elenco_rappresentanti'),
        path('nuovo/', views.RappresentanteCreateView.as_view(), name='nuovo_rappresentante'),
        path('<int:pk>/', views.RappresentanteDetailView.as_view(), name='dettaglio_rappresentante'),
        path('<int:pk>/modifica/', views.RappresentanteUpdateView.as_view(), name='modifica_rappresentante'),
        path('<int:pk>/elimina/', views.RappresentanteDeleteView.as_view(), name='elimina_rappresentante'),
    ])),
    
    # ========== CLIENTI ==========
    path('clienti/', include([
        path('', views.ClienteListView.as_view(), name='elenco_clienti'),
        path('nuovo/', views.ClienteCreateView.as_view(), name='nuovo_cliente'),
        path('<int:pk>/', views.ClienteDetailView.as_view(), name='dettaglio_cliente'),
        path('<int:pk>/modifica/', views.ClienteUpdateView.as_view(), name='modifica_cliente'),
        path('<int:pk>/elimina/', views.ClienteDeleteView.as_view(), name='elimina_cliente'),
    ])),
    
    # ========== FORNITORI ==========
    path('fornitori/', include([
        path('', views.FornitoreListView.as_view(), name='elenco_fornitori'),
        path('nuovo/', views.FornitoreCreateView.as_view(), name='nuovo_fornitore'),
        path('<int:pk>/', views.FornitoreDetailView.as_view(), name='dettaglio_fornitore'),
        path('<int:pk>/modifica/', views.FornitoreUpdateView.as_view(), name='modifica_fornitore'),
        path('<int:pk>/elimina/', views.FornitoreDeleteView.as_view(), name='elimina_fornitore'),
    ])),
    
    # ========== API E UTILITIES ==========
    # Ricerca AJAX
    path('api/search/', views.api_search_anagrafica, name='api_search'),
    
    # Export dati
    path('export/', views.export_anagrafica, name='export_anagrafica'),
    
    # Toggle attivo/inattivo
    path('toggle/<str:tipo>/<int:pk>/', views.toggle_attivo, name='toggle_attivo'),
    
    # ========== API AGGIUNTIVE ==========
    # URL per autocompletamento rappresentanti (da views_extra)
    path('api/rappresentanti/', views_extra.rappresentanti_api, name='rappresentanti_api'),
    
    # URL per statistiche dashboard (da views_extra)
    path('api/stats/', views_extra.dashboard_stats_api, name='dashboard_stats_api'),
    
    # URL per validazione campi (da views_extra)
    path('api/validate/partita-iva/', views_extra.validate_partita_iva, name='validate_partita_iva'),
    path('api/validate/codice-fiscale/', views_extra.validate_codice_fiscale, name='validate_codice_fiscale'),
    
    # URL legacy per retrocompatibilità (se necessario)
    path('vedirappresentante/<int:pk>/', views.RappresentanteDetailView.as_view(), name='vedirappresentante'),
    path('vedicliente/<int:pk>/', views.ClienteDetailView.as_view(), name='vedicliente'),
    path('vedifornitore/<int:pk>/', views.FornitoreDetailView.as_view(), name='vedifornitore'),
]

# Pattern extra per funzionalità avanzate
extra_patterns = [
    # Reports e stampe (da views_extra)
    path('reports/', include([
        path('rappresentanti-pdf/', views_extra.rappresentanti_report_pdf, name='rappresentanti_pdf'),
        path('clienti-pdf/', views_extra.clienti_report_pdf, name='clienti_pdf'),
        path('fornitori-pdf/', views_extra.fornitori_report_pdf, name='fornitori_pdf'),
    ])),
    
    # Import/Export avanzato (da views_extra)
    path('import/', include([
        path('clienti/', views_extra.ImportClientiView.as_view(), name='import_clienti'),
        path('fornitori/', views_extra.ImportFornitoriView.as_view(), name='import_fornitori'),
    ])),
    
    # Operazioni batch (da views_extra)
    path('batch/', include([
        path('attiva-multipli/', views_extra.attiva_multipli, name='attiva_multipli'),
        path('disattiva-multipli/', views_extra.disattiva_multipli, name='disattiva_multipli'),
        path('elimina-multipli/', views_extra.elimina_multipli, name='elimina_multipli'),
    ])),
]

# Aggiungi pattern extra
urlpatterns += extra_patterns
```


## 5. Admin.py

```python
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
```


## 6. Tests.py

```python
import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from django.test.utils import override_settings
from django.core.management import call_command

from dipendenti.models import Dipendente
from .models import Rappresentante, Cliente, Fornitore
from .forms import RappresentanteForm, ClienteForm, FornitoreForm

User = get_user_model()


class AnagraficaModelTests(TestCase):
    """Test per i modelli dell'anagrafica"""
    
    def setUp(self):
        """Setup per ogni test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_rappresentante_creation(self):
        """Test creazione rappresentante valido"""
        rappresentante = Rappresentante.objects.create(
            nome='Mario Rossi',
            ragione_sociale='Test SRL',
            indirizzo='Via Test 123',
            cap='20100',
            città='Milano',
            provincia='MI',
            partita_iva='12345678901',
            codice_fiscale='RSSMRA80A01F205Z',
            telefono='02-1234567',
            email='mario@test.com',
            zona='Nord',
            percentuale_sulle_vendite=5.0
        )
        
        self.assertEqual(str(rappresentante), 'Mario Rossi - Nord')
        self.assertTrue(rappresentante.attivo)
        self.assertIsNotNone(rappresentante.data_creazione)
    
    def test_partita_iva_validation(self):
        """Test validazione partita IVA"""
        rappresentante = Rappresentante(
            nome='Test',
            ragione_sociale='Test SRL',
            partita_iva='123',  # P.IVA non valida
            codice_fiscale='12345678901',
            telefono='123456789',
            email='test@test.com',
            percentuale_sulle_vendite=5.0
        )
        
        with self.assertRaises(ValidationError):
            rappresentante.full_clean()
    
    def test_codice_fiscale_validation(self):
        """Test validazione codice fiscale"""
        rappresentante = Rappresentante(
            nome='Test',
            ragione_sociale='Test SRL',
            partita_iva='12345678901',
            codice_fiscale='INVALID',  # CF non valido
            telefono='123456789',
            email='test@test.com',
            percentuale_sulle_vendite=5.0
        )
        
        with self.assertRaises(ValidationError):
            rappresentante.full_clean()
    
    def test_cliente_with_rappresentante(self):
        """Test creazione cliente con rappresentante"""
        rappresentante = Rappresentante.objects.create(
            nome='Mario Rossi',
            ragione_sociale='Test SRL',
            partita_iva='12345678901',
            codice_fiscale='RSSMRA80A01F205Z',
            telefono='123456789',
            email='mario@test.com',
            percentuale_sulle_vendite=5.0
        )
        
        cliente = Cliente.objects.create(
            rappresentante=rappresentante,
            ragione_sociale='Cliente Test SRL',
            indirizzo='Via Cliente 123',
            cap='20100',
            città='Milano',
            provincia='MI',
            codice_fiscale='12345678901',
            telefono='02-9876543',
            email='cliente@test.com'
        )
        
        self.assertEqual(cliente.rappresentante, rappresentante)
        self.assertIn(cliente, rappresentante.clienti.all())
    
    def test_cliente_without_piva_cf(self):
        """Test cliente senza P.IVA e CF (deve fallire)"""
        cliente = Cliente(
            ragione_sociale='Test',
            # Mancano sia partita_iva che codice_fiscale
            telefono='123456789',
            email='test@test.com'
        )
        
        with self.assertRaises(ValidationError):
            cliente.full_clean()
    
    def test_fornitore_iban_validation(self):
        """Test validazione IBAN fornitore"""
        fornitore = Fornitore(
            ragione_sociale='Fornitore Test SRL',
            codice_fiscale='12345678901',
            telefono='123456789',
            email='fornitore@test.com',
            iban='INVALID_IBAN'  # IBAN non valido
        )
        
        with self.assertRaises(ValidationError):
            fornitore.full_clean()
    
    def test_unique_together_constraints(self):
        """Test vincoli unique_together"""
        # Primo cliente
        Cliente.objects.create(
            ragione_sociale='Test 1',
            partita_iva='12345678901',
            codice_fiscale='12345678901',
            telefono='123456789',
            email='test1@test.com'
        )
        
        # Secondo cliente con stessa P.IVA (deve fallire)
        with self.assertRaises(Exception):  # IntegrityError
            Cliente.objects.create(
                ragione_sociale='Test 2',
                partita_iva='12345678901',  # Duplicato
                codice_fiscale='12345678901',  # Duplicato
                telefono='987654321',
                email='test2@test.com'
            )


class AnagraficaFormTests(TestCase):
    """Test per i form dell'anagrafica"""
    
    def test_rappresentante_form_valid(self):
        """Test form rappresentante valido"""
        form_data = {
            'nome': 'Mario Rossi',
            'ragione_sociale': 'Test SRL',
            'indirizzo': 'Via Test 123',
            'cap': '20100',
            'città': 'Milano',
            'provincia': 'MI',
            'partita_iva': '12345678901',
            'codice_fiscale': 'RSSMRA80A01F205Z',
            'telefono': '02-1234567',
            'email': 'mario@test.com',
            'zona': 'Nord',
            'percentuale_sulle_vendite': 5.0,
            'attivo': True
        }
        
        form = RappresentanteForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_rappresentante_form_invalid_piva(self):
        """Test form rappresentante con P.IVA non valida"""
        form_data = {
            'nome': 'Mario Rossi',
            'ragione_sociale': 'Test SRL',
            'partita_iva': '123',  # P.IVA non valida
            'codice_fiscale': 'RSSMRA80A01F205Z',
            'telefono': '02-1234567',
            'email': 'mario@test.com',
            'percentuale_sulle_vendite': 5.0
        }
        
        form = RappresentanteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('partita_iva', form.errors)
    
    def test_cliente_form_clean_validation(self):
        """Test validazione personalizzata form cliente"""
        # Test senza P.IVA e CF
        form_data = {
            'ragione_sociale': 'Test Cliente',
            'telefono': '123456789',
            'email': 'cliente@test.com'
            # Mancano partita_iva e codice_fiscale
        }
        
        form = ClienteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)


class AnagraficaViewTests(TestCase):
    """Test per le views dell'anagrafica"""
    
    def setUp(self):
        """Setup per ogni test"""
        self.client = Client()
        
        # Crea utenti di test
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@test.com',
            password='testpass123',
            is_staff=True
        )
        
        self.normal_user = User.objects.create_user(
            username='normal',
            email='normal@test.com',
            password='testpass123',
            livello=Dipendente.Autorizzazioni.rappresentante
        )
        
        # Crea rappresentante per il normal_user
        self.rappresentante = Rappresentante.objects.create(
            user=self.normal_user,
            nome='Test Rappresentante',
            ragione_sociale='Test SRL',
            partita_iva='12345678901',
            codice_fiscale='12345678901',
            telefono='123456789',
            email='repr@test.com',
            percentuale_sulle_vendite=5.0
        )
        
        # Crea cliente di test
        self.cliente = Cliente.objects.create(
            rappresentante=self.rappresentante,
            ragione_sociale='Cliente Test',
            codice_fiscale='CLNTEST80A01F205Z',
            telefono='123456789',
            email='cliente@test.com'
        )
    
    def test_dashboard_access(self):
        """Test accesso alla dashboard"""
        # Test senza login
        response = self.client.get(reverse('anagrafica:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect al login
        
        # Test con login
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(reverse('anagrafica:dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_rappresentante_list_staff(self):
        """Test lista rappresentanti per staff"""
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(reverse('anagrafica:elenco_rappresentanti'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.rappresentante.nome)
    
    def test_rappresentante_list_non_staff(self):
        """Test lista rappresentanti per non-staff (deve essere negato)"""
        self.client.login(username='normal', password='testpass123')
        response = self.client.get(reverse('anagrafica:elenco_rappresentanti'))
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_cliente_list_rappresentante(self):
        """Test lista clienti per rappresentante"""
        self.client.login(username='normal', password='testpass123')
        response = self.client.get(reverse('anagrafica:elenco_clienti'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.cliente.ragione_sociale)
    
    def test_cliente_create_staff(self):
        """Test creazione cliente da staff"""
        self.client.login(username='staff', password='testpass123')
        
        form_data = {
            'ragione_sociale': 'Nuovo Cliente',
            'codice_fiscale': '12345678901',
            'telefono': '123456789',
            'email': 'nuovo@test.com',
            'pagamento': '01'
        }
        
        response = self.client.post(reverse('anagrafica:nuovo_cliente'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect dopo creazione
        self.assertTrue(Cliente.objects.filter(ragione_sociale='Nuovo Cliente').exists())
    
    def test_cliente_detail_access_control(self):
        """Test controllo accesso dettaglio cliente"""
        # Crea altro rappresentante e cliente
        altro_user = User.objects.create_user(
            username='altro', 
            password='testpass123',
            livello=Dipendente.Autorizzazioni.rappresentante
        )
        altro_repr = Rappresentante.objects.create(
            user=altro_user,
            nome='Altro',
            ragione_sociale='Altro SRL',
            partita_iva='98765432109',
            codice_fiscale='98765432109',
            telefono='987654321',
            email='altro@test.com',
            percentuale_sulle_vendite=5.0
        )
        altro_cliente = Cliente.objects.create(
            rappresentante=altro_repr,
            ragione_sociale='Cliente Altro',
            codice_fiscale='ALTRO80A01F205Z',
            telefono='987654321',
            email='altro.cliente@test.com'
        )
        
        # Il normal_user non dovrebbe vedere il cliente dell'altro rappresentante
        self.client.login(username='normal', password='testpass123')
        response = self.client.get(reverse('anagrafica:dettaglio_cliente', args=[altro_cliente.id]))
        self.assertEqual(response.status_code, 404)  # Not found per sicurezza


class AnagraficaAPITests(TestCase):
    """Test per le API dell'anagrafica"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Crea dati di test
        self.rappresentante = Rappresentante.objects.create(
            nome='Test Rappresentante',
            ragione_sociale='Test SRL',
            partita_iva='12345678901',
            codice_fiscale='12345678901',
            telefono='123456789',
            email='test@test.com',
            percentuale_sulle_vendite=5.0
        )
    
    def test_search_api(self):
        """Test API di ricerca"""
        response = self.client.get(reverse('anagrafica:api_search'), {'q': 'Test'})
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('results', data)
        self.assertTrue(len(data['results']) > 0)
    
    def test_validate_partita_iva_api(self):
        """Test API validazione partita IVA"""
        # Test P.IVA valida
        response = self.client.get(reverse('anagrafica:validate_partita_iva'), {
            'partita_iva': '12345678901',
            'tipo': 'cliente'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['valid'])  # Già esistente
        
        # Test P.IVA non valida
        response = self.client.get(reverse('anagrafica:validate_partita_iva'), {
            'partita_iva': '123',
            'tipo': 'cliente'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['valid'])
        self.assertIn('11 cifre', data['message'])


class AnagraficaManagementCommandTests(TestCase):
    """Test per i command di management"""
    
    def test_setup_anagrafica_command(self):
        """Test comando setup_anagrafica"""
        # Test senza dati di esempio
        call_command('setup_anagrafica')
        
        # Verifica creazione gruppi
        self.assertTrue(Group.objects.filter(name='Gestori Anagrafica').exists())
        self.assertTrue(Group.objects.filter(name='Rappresentanti').exists())
    
    def test_setup_with_sample_data(self):
        """Test comando con dati di esempio"""
        call_command('setup_anagrafica', '--create-sample-data')
        
        # Verifica creazione dati
        self.assertTrue(Rappresentante.objects.exists())
        self.assertTrue(Cliente.objects.exists())
        self.assertTrue(Fornitore.objects.exists())


class AnagraficaSignalTests(TestCase):
    """Test per i segnali"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            livello=Dipendente.Autorizzazioni.rappresentante
        )
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_rappresentante_creation_signal(self):
        """Test segnale creazione rappresentante"""
        # Crea admin per ricevere notifica
        admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='adminpass',
            is_staff=True
        )
        
        # Crea rappresentante
        rappresentante = Rappresentante.objects.create(
            user=self.user,
            nome='Test Signal',
            ragione_sociale='Test SRL',
            partita_iva='12345678901',
            codice_fiscale='12345678901',
            telefono='123456789',
            email='signal@test.com',
            percentuale_sulle_vendite=5.0
        )
        
        # Verifica invio email (in memoria)
        from django.core import mail
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Nuovo Rappresentante', mail.outbox[0].subject)


if __name__ == '__main__':
    unittest.main()
```


## 7. Signals.py

```python
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
```


## 8. Templates


### dashboard.html

```html
{% extends 'base.html' %}
{% load static %}

{% block title %}Dashboard Anagrafica{% endblock %}

{% block extra_css %}
<style>
    .stat-card {
        transition: transform 0.3s ease;
    }
    .stat-card:hover {
        transform: translateY(-5px);
    }
    .icon-large {
        font-size: 2.5rem;
    }
</style>
{% endblock %}

{% block content %}
<div class="container-fluid">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h1 class="h3 mb-0 text-gray-800">Dashboard Anagrafica</h1>
        <div class="btn-group" role="group">
            <button type="button" class="btn btn-primary dropdown-toggle" data-bs-toggle="dropdown">
                <i class="fas fa-plus"></i> Aggiungi
            </button>
            <ul class="dropdown-menu">
                <li><a class="dropdown-item" href="{% url 'anagrafica:nuovo_rappresentante' %}">
                    <i class="fas fa-user-tie"></i> Nuovo Rappresentante</a></li>
                <li><a class="dropdown-item" href="{% url 'anagrafica:nuovo_cliente' %}">
                    <i class="fas fa-building"></i> Nuovo Cliente</a></li>
                <li><a class="dropdown-item" href="{% url 'anagrafica:nuovo_fornitore' %}">
                    <i class="fas fa-truck"></i> Nuovo Fornitore</a></li>
            </ul>
        </div>
    </div>

    <!-- Statistics Cards -->
    <div class="row mb-4">
        <div class="col-xl-3 col-md-6 mb-4">
            <div class="card stat-card border-left-primary shadow h-100 py-2">
                <div class="card-body">
                    <div class="row no-gutters align-items-center">
                        <div class="col mr-2">
                            <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">
                                Rappresentanti Attivi
                            </div>
                            <div class="h5 mb-0 font-weight-bold text-gray-800">{{ rappresentanti_count }}</div>
                        </div>
                        <div class="col-auto">
                            <i class="fas fa-user-tie fa-2x text-gray-300"></i>
                        </div>
                    </div>
                </div>
                <div class="card-footer d-flex align-items-center justify-content-between">
                    <a class="small text-primary" href="{% url 'anagrafica:elenco_rappresentanti' %}">Visualizza Dettagli</a>
                    <div class="small text-primary">
                        <i class="fas fa-angle-right"></i>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-xl-3 col-md-6 mb-4">
            <div class="card stat-card border-left-success shadow h-100 py-2">
                <div class="card-body">
                    <div class="row no-gutters align-items-center">
                        <div class="col mr-2">
                            <div class="text-xs font-weight-bold text-success text-uppercase mb-1">
                                Clienti Attivi
                            </div>
                            <div class="h5 mb-0 font-weight-bold text-gray-800">{{ clienti_count }}</div>
                        </div>
                        <div class="col-auto">
                            <i class="fas fa-building fa-2x text-gray-300"></i>
                        </div>
                    </div>
                </div>
                <div class="card-footer d-flex align-items-center justify-content-between">
                    <a class="small text-success" href="{% url 'anagrafica:elenco_clienti' %}">Visualizza Dettagli</a>
                    <div class="small text-success">
                        <i class="fas fa-angle-right"></i>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-xl-3 col-md-6 mb-4">
            <div class="card stat-card border-left-info shadow h-100 py-2">
                <div class="card-body">
                    <div class="row no-gutters align-items-center">
                        <div class="col mr-2">
                            <div class="text-xs font-weight-bold text-info text-uppercase mb-1">
                                Fornitori Attivi
                            </div>
                            <div class="h5 mb-0 font-weight-bold text-gray-800">{{ fornitori_count }}</div>
                        </div>
                        <div class="col-auto">
                            <i class="fas fa-truck fa-2x text-gray-300"></i>
                        </div>
                    </div>
                </div>
                <div class="card-footer d-flex align-items-center justify-content-between">
                    <a class="small text-info" href="{% url 'anagrafica:elenco_fornitori' %}">Visualizza Dettagli</a>
                    <div class="small text-info">
                        <i class="fas fa-angle-right"></i>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-xl-3 col-md-6 mb-4">
            <div class="card stat-card border-left-warning shadow h-100 py-2">
                <div class="card-body">
                    <div class="row no-gutters align-items-center">
                        <div class="col mr-2">
                            <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">
                                Rappresentanti Senza Clienti
                            </div>
                            <div class="h5 mb-0 font-weight-bold text-gray-800">{{ rappresentanti_senza_clienti }}</div>
                        </div>
                        <div class="col-auto">
                            <i class="fas fa-exclamation-triangle fa-2x text-gray-300"></i>
                        </div>
                    </div>
                </div>
                <div class="card-footer d-flex align-items-center justify-content-between">
                    <a class="small text-warning" href="{% url 'anagrafica:elenco_rappresentanti' %}?has_clients=no">Visualizza</a>
                    <div class="small text-warning">
                        <i class="fas fa-angle-right"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Recent Activities -->
    <div class="row">
        <!-- Recent Rappresentanti -->
        <div class="col-lg-4 mb-4">
            <div class="card shadow">
                <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                    <h6 class="m-0 font-weight-bold text-primary">Rappresentanti Recenti</h6>
                    <a href="{% url 'anagrafica:elenco_rappresentanti' %}" class="btn btn-sm btn-primary">
                        <i class="fas fa-eye"></i> Vedi Tutti
                    </a>
                </div>
                <div class="card-body">
                    {% for rappresentante in recent_rappresentanti %}
                    <div class="d-flex align-items-center mb-3">
                        <div class="mr-3">
                            <div class="icon-circle bg-primary">
                                <i class="fas fa-user-tie text-white"></i>
                            </div>
                        </div>
                        <div>
                            <div class="small text-gray-500">{{ rappresentante.data_creazione|date:"d/m/Y" }}</div>
                            <a href="{% url 'anagrafica:dettaglio_rappresentante' rappresentante.pk %}" class="font-weight-bold">
                                {{ rappresentante.nome }}
                            </a>
                            <div class="small text-muted">{{ rappresentante.zona|default:"Zona non specificata" }}</div>
                        </div>
                    </div>
                    {% empty %}
                    <p class="text-muted">Nessun rappresentante aggiunto di recente</p>
                    {% endfor %}
                </div>
            </div>
        </div>

        <!-- Recent Clienti -->
        <div class="col-lg-4 mb-4">
            <div class="card shadow">
                <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                    <h6 class="m-0 font-weight-bold text-success">Clienti Recenti</h6>
                    <a href="{% url 'anagrafica:elenco_clienti' %}" class="btn btn-sm btn-success">
                        <i class="fas fa-eye"></i> Vedi Tutti
                    </a>
                </div>
                <div class="card-body">
                    {% for cliente in recent_clienti %}
                    <div class="d-flex align-items-center mb-3">
                        <div class="mr-3">
                            <div class="icon-circle bg-success">
                                <i class="fas fa-building text-white"></i>
                            </div>
                        </div>
                        <div>
                            <div class="small text-gray-500">{{ cliente.data_creazione|date:"d/m/Y" }}</div>
                            <a href="{% url 'anagrafica:dettaglio_cliente' cliente.pk %}" class="font-weight-bold">
                                {{ cliente.ragione_sociale }}
                            </a>
                            <div class="small text-muted">{{ cliente.città }}</div>
                        </div>
                    </div>
                    {% empty %}
                    <p class="text-muted">Nessun cliente aggiunto di recente</p>
                    {% endfor %}
                </div>
            </div>
        </div>

        <!-- Recent Fornitori -->
        <div class="col-lg-4 mb-4">
            <div class="card shadow">
                <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                    <h6 class="m-0 font-weight-bold text-info">Fornitori Recenti</h6>
                    <a href="{% url 'anagrafica:elenco_fornitori' %}" class="btn btn-sm btn-info">
                        <i class="fas fa-eye"></i> Vedi Tutti
                    </a>
                </div>
                <div class="card-body">
                    {% for fornitore in recent_fornitori %}
                    <div class="d-flex align-items-center mb-3">
                        <div class="mr-3">
                            <div class="icon-circle bg-info">
                                <i class="fas fa-truck text-white"></i>
                            </div>
                        </div>
                        <div>
                            <div class="small text-gray-500">{{ fornitore.data_creazione|date:"d/m/Y" }}</div>
                            <a href="{% url 'anagrafica:dettaglio_fornitore' fornitore.pk %}" class="font-weight-bold">
                                {{ fornitore.ragione_sociale }}
                            </a>
                            <div class="small text-muted">{{ fornitore.categoria|default:"Categoria non specificata" }}</div>
                        </div>
                    </div>
                    {% empty %}
                    <p class="text-muted">Nessun fornitore aggiunto di recente</p>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>

    <!-- Quick Actions -->
    <div class="row">
        <div class="col-12">
            <div class="card shadow">
                <div class="card-header py-3">
                    <h6 class="m-0 font-weight-bold text-primary">Azioni Rapide</h6>
                </div>
                <div class="card-body">
                    <div class="row text-center">
                        <div class="col-md-3 mb-3">
                            <a href="{% url 'anagrafica:api_search' %}" class="btn btn-outline-primary btn-lg d-block">
                                <i class="fas fa-search fa-2x mb-2"></i>
                                <br>Ricerca Globale
                            </a>
                        </div>
                        <div class="col-md-3 mb-3">
                            <a href="{% url 'anagrafica:export_anagrafica' %}" class="btn btn-outline-success btn-lg d-block">
                                <i class="fas fa-download fa-2x mb-2"></i>
                                <br>Export Dati
                            </a>
                        </div>
                        <div class="col-md-3 mb-3">
                            <a href="#" class="btn btn-outline-info btn-lg d-block" onclick="printReports()">
                                <i class="fas fa-file-pdf fa-2x mb-2"></i>
                                <br>Reports PDF
                            </a>
                        </div>
                        <div class="col-md-3 mb-3">
                            <a href="#" class="btn btn-outline-warning btn-lg d-block" onclick="showStats()">
                                <i class="fas fa-chart-bar fa-2x mb-2"></i>
                                <br>Statistiche
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
function printReports() {
    // Dropdown per scegliere tipo di report
    const reportTypes = [
        { name: 'Rappresentanti', url: '{% url "anagrafica:rappresentanti_pdf" %}' },
        { name: 'Clienti', url: '{% url "anagrafica:clienti_pdf" %}' },
        { name: 'Fornitori', url: '{% url "anagrafica:fornitori_pdf" %}' }
    ];
    
    let options = reportTypes.map(report => 
        `<li><a class="dropdown-item" href="${report.url}">${report.name}</a></li>`
    ).join('');
    
    // Crea dropdown temporaneo
    const dropdown = document.createElement('div');
    dropdown.innerHTML = `
        <div class="btn-group dropup">
            <button class="btn btn-outline-info dropdown-toggle" type="button" data-bs-toggle="dropdown">
                Scegli Report
            </button>
            <ul class="dropdown-menu">${options}</ul>
        </div>
    `;
    
    document.body.appendChild(dropdown);
    dropdown.querySelector('button').click();
}

function showStats() {
    // Chiamata AJAX per statistics aggiornate
    fetch('{% url "anagrafica:dashboard_stats_api" %}')
        .then(response => response.json())
        .then(data => {
            const statsHtml = `
                <div class="modal fade" id="statsModal" tabindex="-1">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Statistiche Anagrafica</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="row">
                                    <div class="col-md-4">
                                        <h6>Rappresentanti</h6>
                                        <p>Totali: ${data.rappresentanti.totali}</p>
                                        <p>Attivi: ${data.rappresentanti.attivi}</p>
                                    </div>
                                    <div class="col-md-4">
                                        <h6>Clienti</h6>
                                        <p>Totali: ${data.clienti.totali}</p>
                                        <p>Attivi: ${data.clienti.attivi}</p>
                                    </div>
                                    <div class="col-md-4">
                                        <h6>Fornitori</h6>
                                        <p>Totali: ${data.fornitori.totali}</p>
                                        <p>Attivi: ${data.fornitori.attivi}</p>
                                    </div>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Chiudi</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.insertAdjacentHTML('beforeend', statsHtml);
            new bootstrap.Modal(document.getElementById('statsModal')).show();
        });
}
</script>
{% endblock %}
```


### nuovo.html

```html
{% extends 'base.html' %}
{% load static %}
{% load crispy_forms_tags %}

{% block title %}
{% if cliente.pk %}Modifica Cliente{% else %}Nuovo Cliente{% endif %}
{% endblock %}

{% block extra_css %}
<style>
    .form-container {
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        padding: 2rem;
    }
    
    .step-indicator {
        background: linear-gradient(45deg, #2ecc71 0%, #3498db 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .tab-content {
        padding: 1.5rem 0;
    }
    
    .nav-tabs .nav-link {
        border: none;
        border-radius: 25px;
        margin-right: 0.5rem;
        padding: 0.75rem 1.5rem;
        color: #2ecc71;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .nav-tabs .nav-link:hover {
        background-color: rgba(46, 204, 113, 0.1);
        color: #27ae60;
    }
    
    .nav-tabs .nav-link.active {
        background: linear-gradient(45deg, #2ecc71 0%, #3498db 100%);
        color: white;
        border-color: transparent;
    }
    
    .form-group label {
        color: #495057;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .form-control, .form-select {
        border: 2px solid #e9ecef;
        border-radius: 8px;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .form-control:focus, .form-select:focus {
        border-color: #2ecc71;
        box-shadow: 0 0 0 0.2rem rgba(46, 204, 113, 0.25);
    }
    
    .btn-primary {
        background: linear-gradient(45deg, #2ecc71 0%, #3498db 100%);
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(46, 204, 113, 0.3);
    }
    
    .btn-secondary {
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
    }
    
    .required-field::after {
        content: ' *';
        color: #dc3545;
    }
    
    .field-help {
        font-size: 0.875rem;
        color: #6c757d;
        margin-top: 0.25rem;
    }
    
    .validation-message {
        background-color: #f8f9fa;
        border: 1px solid #e2e2e8;
        border-radius: 8px;
        padding: 0.75rem;
        margin-top: 0.5rem;
        font-size: 0.875rem;
    }
    
    .validation-message.valid {
        border-color: #28a745;
        color: #155724;
        background-color: #d4edda;
    }
    
    .validation-message.invalid {
        border-color: #dc3545;
        color: #721c24;
        background-color: #f8d7da;
    }
    
    .quick-fill-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .rappresentante-info {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 0.5rem;
        border-left: 4px solid #2ecc71;
    }
    
    .validation-pills {
        display: flex;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }
    
    .validation-pill {
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    .validation-pill.valid {
        background-color: #d4edda;
        color: #155724;
    }
    
    .validation-pill.invalid {
        background-color: #f8d7da;
        color: #721c24;
    }
    
    .validation-pill.checking {
        background-color: #fff3cd;
        color: #856404;
    }
</style>
{% endblock %}

{% block content %}
<div class="container-fluid">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="{% url 'anagrafica:dashboard' %}">Anagrafica</a></li>
                    <li class="breadcrumb-item"><a href="{% url 'anagrafica:elenco_clienti' %}">Clienti</a></li>
                    <li class="breadcrumb-item active">
                        {% if cliente.pk %}Modifica{% else %}Nuovo{% endif %}
                    </li>
                </ol>
            </nav>
            <h1 class="h3 mb-0">
                {% if cliente.pk %}
                    <i class="fas fa-edit"></i> Modifica Cliente
                {% else %}
                    <i class="fas fa-plus"></i> Nuovo Cliente
                {% endif %}
            </h1>
        </div>
        {% if request.GET.rappresentante %}
        <div class="quick-fill-card">
            <div class="d-flex align-items-center">
                <i class="fas fa-user-tie fa-2x me-3"></i>
                <div>
                    <h6 class="mb-0">Assegnato a:</h6>
                    <p class="mb-0">Rappresentante preselezionato</p>
                </div>
            </div>
        </div>
        {% endif %}
    </div>

    <!-- Step Indicator -->
    <div class="step-indicator">
        <h4 class="mb-0">
            {% if cliente.pk %}
                Modifica i dati del cliente {{ cliente.ragione_sociale }}
            {% else %}
                Inserimento nuovo cliente
            {% endif %}
        </h4>
        <p class="mb-0 mt-2 opacity-75">
            {% if not cliente.pk %}
            <i class="fas fa-exclamation-circle"></i> 
            Inserire almeno uno tra Partita IVA e Codice Fiscale
            {% else %}
            Modifica i dati e salva le modifiche
            {% endif %}
        </p>
    </div>

    <!-- Form Container -->
    <div class="form-container">
        <form method="post" id="clienteForm">
            {% csrf_token %}
            
            <!-- Form Errors (if any) -->
            {% if form.non_field_errors %}
            <div class="alert alert-danger" role="alert">
                <h5 class="alert-heading"><i class="fas fa-exclamation-triangle"></i> Errori di validazione</h5>
                {% for error in form.non_field_errors %}
                    <p class="mb-0">{{ error }}</p>
                {% endfor %}
            </div>
            {% endif %}
            
            <!-- Tabs Navigation -->
            <ul class="nav nav-tabs" id="formTabs" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="general-tab" data-bs-toggle="tab" 
                            data-bs-target="#general" type="button" role="tab">
                        <i class="fas fa-building"></i> Informazioni Generali
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="fiscal-tab" data-bs-toggle="tab" 
                            data-bs-target="#fiscal" type="button" role="tab">
                        <i class="fas fa-id-card"></i> Dati Fiscali
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="contacts-tab" data-bs-toggle="tab" 
                            data-bs-target="#contacts" type="button" role="tab">
                        <i class="fas fa-phone"></i> Contatti
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="commercial-tab" data-bs-toggle="tab" 
                            data-bs-target="#commercial" type="button" role="tab">
                        <i class="fas fa-handshake"></i> Condizioni Commerciali
                    </button>
                </li>
            </ul>
            
            <!-- Tab Content -->
            <div class="tab-content" id="formTabContent">
                <!-- Tab 1: Informazioni Generali -->
                <div class="tab-pane fade show active" id="general" role="tabpanel">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.rappresentante.id_for_label }}" class="form-label">
                                    Rappresentante di Riferimento
                                </label>
                                {{ form.rappresentante }}
                                {% if form.rappresentante.errors %}
                                    <div class="text-danger mt-1">{{ form.rappresentante.errors|join:', ' }}</div>
                                {% endif %}
                                <div class="field-help">Seleziona il rappresentante che gestirà questo cliente</div>
                                <div id="rappresentante-info" class="rappresentante-info d-none">
                                    <div class="d-flex align-items-center">
                                        <i class="fas fa-user-tie text-success me-2"></i>
                                        <div>
                                            <strong id="rappresentante-nome"></strong>
                                            <br>
                                            <small class="text-muted">
                                                <span id="rappresentante-zona"></span> | 
                                                <span id="rappresentante-email"></span>
                                            </small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.zona.id_for_label }}" class="form-label">
                                    Zona Geografica
                                </label>
                                {{ form.zona }}
                                {% if form.zona.errors %}
                                    <div class="text-danger mt-1">{{ form.zona.errors|join:', ' }}</div>
                                {% endif %}
                                <div class="field-help">Zona di pertinenza del cliente</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-12">
                            <div class="mb-3">
                                <label for="{{ form.ragione_sociale.id_for_label }}" class="form-label required-field">
                                    Ragione Sociale
                                </label>
                                {{ form.ragione_sociale }}
                                {% if form.ragione_sociale.errors %}
                                    <div class="text-danger mt-1">{{ form.ragione_sociale.errors|join:', ' }}</div>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-8">
                            <div class="mb-3">
                                <label for="{{ form.indirizzo.id_for_label }}" class="form-label">
                                    Indirizzo
                                </label>
                                {{ form.indirizzo }}
                                {% if form.indirizzo.errors %}
                                    <div class="text-danger mt-1">{{ form.indirizzo.errors|join:', ' }}</div>
                                {% endif %}
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="mb-3">
                                <label for="{{ form.cap.id_for_label }}" class="form-label">
                                    CAP
                                </label>
                                {{ form.cap }}
                                {% if form.cap.errors %}
                                    <div class="text-danger mt-1">{{ form.cap.errors|join:', ' }}</div>
                                {% endif %}
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="mb-3">
                                <label for="{{ form.provincia.id_for_label }}" class="form-label">
                                    Provincia
                                </label>
                                {{ form.provincia }}
                                {% if form.provincia.errors %}
                                    <div class="text-danger mt-1">{{ form.provincia.errors|join:', ' }}</div>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-12">
                            <div class="mb-3">
                                <label for="{{ form.città.id_for_label }}" class="form-label">
                                    Città
                                </label>
                                {{ form.città }}
                                {% if form.città.errors %}
                                    <div class="text-danger mt-1">{{ form.città.errors|join:', ' }}</div>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Tab 2: Dati Fiscali -->
                <div class="tab-pane fade" id="fiscal" role="tabpanel">
                    <div class="alert alert-warning" role="alert">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        <strong>Attenzione:</strong> È obbligatorio inserire almeno uno tra Partita IVA e Codice Fiscale
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.partita_iva.id_for_label }}" class="form-label">
                                    Partita IVA
                                </label>
                                {{ form.partita_iva }}
                                {% if form.partita_iva.errors %}
                                    <div class="text-danger mt-1">{{ form.partita_iva.errors|join:', ' }}</div>
                                {% endif %}
                                <div class="validation-pills">
                                    <div class="validation-pill d-none" id="piva-validation"></div>
                                </div>
                                <div class="field-help">11 cifre numeriche (opzionale per i clienti)</div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.codice_fiscale.id_for_label }}" class="form-label">
                                    Codice Fiscale
                                </label>
                                {{ form.codice_fiscale }}
                                {% if form.codice_fiscale.errors %}
                                    <div class="text-danger mt-1">{{ form.codice_fiscale.errors|join:', ' }}</div>
                                {% endif %}
                                <div class="validation-pills">
                                    <div class="validation-pill d-none" id="cf-validation"></div>
                                </div>
                                <div class="field-help">16 caratteri per persona fisica, 11 cifre per azienda</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.codice_univoco.id_for_label }}" class="form-label">
                                    Codice Univoco
                                </label>
                                {{ form.codice_univoco }}
                                {% if form.codice_univoco.errors %}
                                    <div class="text-danger mt-1">{{ form.codice_univoco.errors|join:', ' }}</div>
                                {% endif %}
                                <div class="field-help">Codice destinatario per fatturazione elettronica</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Tab 3: Contatti -->
                <div class="tab-pane fade" id="contacts" role="tabpanel">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.telefono.id_for_label }}" class="form-label required-field">
                                    Telefono
                                </label>
                                {{ form.telefono }}
                                {% if form.telefono.errors %}
                                    <div class="text-danger mt-1">{{ form.telefono.errors|join:', ' }}</div>
                                {% endif %}
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.email.id_for_label }}" class="form-label required-field">
                                    Email
                                </label>
                                {{ form.email }}
                                {% if form.email.errors %}
                                    <div class="text-danger mt-1">{{ form.email.errors|join:', ' }}</div>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Tab 4: Condizioni Commerciali -->
                <div class="tab-pane fade" id="commercial" role="tabpanel">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.pagamento.id_for_label }}" class="form-label">
                                    Modalità di Pagamento
                                </label>
                                {{ form.pagamento }}
                                {% if form.pagamento.errors %}
                                    <div class="text-danger mt-1">{{ form.pagamento.errors|join:', ' }}</div>
                                {% endif %}
                                <div class="field-help">Termini di pagamento predefiniti per questo cliente</div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.limite_credito.id_for_label }}" class="form-label">
                                    Limite di Credito (€)
                                </label>
                                {{ form.limite_credito }}
                                {% if form.limite_credito.errors %}
                                    <div class="text-danger mt-1">{{ form.limite_credito.errors|join:', ' }}</div>
                                {% endif %}
                                <div class="field-help">Importo massimo di credito concedibile</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.sconto_percentuale.id_for_label }}" class="form-label">
                                    Sconto Percentuale (%)
                                </label>
                                {{ form.sconto_percentuale }}
                                {% if form.sconto_percentuale.errors %}
                                    <div class="text-danger mt-1">{{ form.sconto_percentuale.errors|join:', ' }}</div>
                                {% endif %}
                                <div class="field-help">Sconto predefinito applicato a questo cliente</div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3 d-flex align-items-center">
                                <div class="form-check">
                                    {{ form.attivo }}
                                    <label class="form-check-label" for="{{ form.attivo.id_for_label }}">
                                        Cliente Attivo
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-12">
                            <div class="mb-3">
                                <label for="{{ form.note.id_for_label }}" class="form-label">
                                    Note Aggiuntive
                                </label>
                                {{ form.note }}
                                {% if form.note.errors %}
                                    <div class="text-danger mt-1">{{ form.note.errors|join:', ' }}</div>
                                {% endif %}
                                <div class="field-help">Note interne relative al cliente</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Footer Buttons -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="d-flex justify-content-between">
                        <a href="{% url 'anagrafica:elenco_clienti' %}" class="btn btn-secondary">
                            <i class="fas fa-arrow-left"></i> Annulla
                        </a>
                        <div>
                            <button type="button" class="btn btn-outline-primary me-2" id="preview-btn">
                                <i class="fas fa-eye"></i> Anteprima
                            </button>
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save"></i>
                                {% if cliente.pk %}Aggiorna{% else %}Salva{% endif %} Cliente
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </form>
    </div>
    
    <!-- Preview Modal -->
    <div class="modal fade" id="previewModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Anteprima Cliente</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="preview-content">
                    <!-- Content will be generated via JavaScript -->
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Chiudi</button>
                    <button type="button" class="btn btn-primary" onclick="document.getElementById('clienteForm').submit();">
                        <i class="fas fa-save"></i> Conferma e Salva
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Precompile rappresentante info if coming from rappresentante detail
    {% if request.GET.rappresentante %}
    const rappresentanteSelect = document.getElementById('{{ form.rappresentante.id_for_label }}');
    if (rappresentanteSelect) {
        rappresentanteSelect.value = '{{ request.GET.rappresentante }}';
        rappresentanteSelect.dispatchEvent(new Event('change'));
    }
    {% endif %}
    
    // Rappresentante change handler
    const rappresentanteSelect = document.getElementById('{{ form.rappresentante.id_for_label }}');
    const rappresentanteInfo = document.getElementById('rappresentante-info');
    
    if (rappresentanteSelect) {
        rappresentanteSelect.addEventListener('change', function() {
            if (this.value) {
                // Fetch rappresentante info via AJAX
                fetch(`{% url 'anagrafica:rappresentanti_api' %}?term=${this.value}`)
                .then(response => response.json())
                .then(data => {
                    if (data.results && data.results.length > 0) {
                        const repr = data.results[0];
                        document.getElementById('rappresentante-nome').textContent = repr.text;
                        document.getElementById('rappresentante-zona').textContent = 'Zona';
                        document.getElementById('rappresentante-email').textContent = 'Email';
                        rappresentanteInfo.classList.remove('d-none');
                    }
                });
            } else {
                rappresentanteInfo.classList.add('d-none');
            }
        });
    }
    
    // Real-time P.IVA validation
    const pivaField = document.getElementById('{{ form.partita_iva.id_for_label }}');
    const pivaValidation = document.getElementById('piva-validation');
    
    if (pivaField) {
        pivaField.addEventListener('blur', function() {
            const piva = this.value.trim();
            if (piva && piva.length === 11) {
                pivaValidation.className = 'validation-pill checking';
                pivaValidation.textContent = 'Verifica in corso...';
                pivaValidation.classList.remove('d-none');
                
                fetch('{% url "anagrafica:validate_partita_iva" %}?' + new URLSearchParams({
                    partita_iva: piva,
                    tipo: 'cliente',
                    exclude_id: '{{ cliente.pk|default:"" }}'
                }))
                .then(response => response.json())
                .then(data => {
                    pivaValidation.textContent = data.message;
                    pivaValidation.className = 'validation-pill ' + (data.valid ? 'valid' : 'invalid');
                });
            } else if (piva && piva.length !== 11) {
                pivaValidation.className = 'validation-pill invalid';
                pivaValidation.textContent = 'Deve essere di 11 cifre';
                pivaValidation.classList.remove('d-none');
            } else {
                pivaValidation.classList.add('d-none');
            }
        });
    }
    
    // Real-time CF validation
    const cfField = document.getElementById('{{ form.codice_fiscale.id_for_label }}');
    const cfValidation = document.getElementById('cf-validation');
    
    if (cfField) {
        cfField.addEventListener('blur', function() {
            const cf = this.value.trim().toUpperCase();
            this.value = cf; // Auto-uppercase
            
            if (cf && (cf.length === 11 || cf.length === 16)) {
                cfValidation.className = 'validation-pill checking';
                cfValidation.textContent = 'Verifica in corso...';
                cfValidation.classList.remove('d-none');
                
                fetch('{% url "anagrafica:validate_codice_fiscale" %}?' + new URLSearchParams({
                    codice_fiscale: cf,
                    tipo: 'cliente',
                    exclude_id: '{{ cliente.pk|default:"" }}'
                }))
                .then(response => response.json())
                .then(data => {
                    cfValidation.textContent = data.message;
                    cfValidation.className = 'validation-pill ' + (data.valid ? 'valid' : 'invalid');
                });
            } else if (cf && cf.length !== 11 && cf.length !== 16) {
                cfValidation.className = 'validation-pill invalid';
                cfValidation.textContent = 'Deve essere di 11 o 16 caratteri';
                cfValidation.classList.remove('d-none');
            } else {
                cfValidation.classList.add('d-none');
            }
        });
    }
    
    // Auto-uppercase provincia field
    const provinciaField = document.getElementById('{{ form.provincia.id_for_label }}');
    if (provinciaField) {
        provinciaField.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
        });
    }
    
    // Check if P.IVA/CF required validation
    function checkPivaCfRequired() {
        const piva = document.getElementById('{{ form.partita_iva.id_for_label }}').value.trim();
        const cf = document.getElementById('{{ form.codice_fiscale.id_for_label }}').value.trim();
        
        if (!piva && !cf) {
            return false;
        }
        return true;
    }
    
    // Preview functionality
    document.getElementById('preview-btn').addEventListener('click', function() {
        const formData = new FormData(document.getElementById('clienteForm'));
        const previewContent = document.getElementById('preview-content');
        
        let html = '<div class="preview-container">';
        html += '<h6 class="mb-3"><i class="fas fa-building"></i> Informazioni Generali</h6>';
        html += '<p><strong>Ragione Sociale:</strong> ' + (formData.get('ragione_sociale') || 'Non specificato') + '</p>';
        html += '<p><strong>Indirizzo:</strong> ' + (formData.get('indirizzo') || 'Non specificato') + '</p>';
        html += '<p><strong>Città:</strong> ' + (formData.get('città') || 'Non specificato') + ' (' + (formData.get('provincia') || 'N/A') + ') ' + (formData.get('cap') || '') + '</p>';
        
        html += '<h6 class="mt-4 mb-3"><i class="fas fa-id-card"></i> Dati Fiscali</h6>';
        html += '<p><strong>Partita IVA:</strong> ' + (formData.get('partita_iva') || 'Non presente') + '</p>';
        html += '<p><strong>Codice Fiscale:</strong> ' + (formData.get('codice_fiscale') || 'Non presente') + '</p>';
        
        html += '<h6 class="mt-4 mb-3"><i class="fas fa-phone"></i> Contatti</h6>';
        html += '<p><strong>Email:</strong> ' + (formData.get('email') || 'Non specificato') + '</p>';
        html += '<p><strong>Telefono:</strong> ' + (formData.get('telefono') || 'Non specificato') + '</p>';
        
        html += '<h6 class="mt-4 mb-3"><i class="fas fa-handshake"></i> Condizioni Commerciali</h6>';
        html += '<p><strong>Modalità Pagamento:</strong> ' + (formData.get('pagamento') || 'Immediato') + '</p>';
        if (formData.get('limite_credito')) {
            html += '<p><strong>Limite Credito:</strong> €' + formData.get('limite_credito') + '</p>';
        }
        if (formData.get('sconto_percentuale')) {
            html += '<p><strong>Sconto:</strong> ' + formData.get('sconto_percentuale') + '%</p>';
        }
        html += '<p><strong>Stato:</strong> ' + (formData.get('attivo') === 'on' ? 'Attivo' : 'Non attivo') + '</p>';
        html += '</div>';
        
        previewContent.innerHTML = html;
        new bootstrap.Modal(document.getElementById('previewModal')).show();
    });
    
    // Tab validation
    function validateTab(tabId) {
        const tab = document.getElementById(tabId);
        const inputs = tab.querySelectorAll('input[required], select[required]');
        let isValid = true;
        
        // Special validation for fiscal tab
        if (tabId === 'fiscal') {
            const piva = document.getElementById('{{ form.partita_iva.id_for_label }}').value.trim();
            const cf = document.getElementById('{{ form.codice_fiscale.id_for_label }}').value.trim();
            
            if (!piva && !cf) {
                isValid = false;
                alert('Inserire almeno uno tra Partita IVA e Codice Fiscale');
            }
        }
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                input.classList.add('is-invalid');
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    }
    
    // Navigation between tabs with validation
    document.querySelectorAll('#formTabs button[data-bs-toggle="tab"]').forEach(button => {
        button.addEventListener('click', function(e) {
            const currentTab = document.querySelector('.tab-pane.active');
            if (currentTab && !validateTab(currentTab.id)) {
                e.preventDefault();
                // Don't prevent navigation for validation, just show warning
            }
        });
    });
    
    // Form submission validation
    document.getElementById('clienteForm').addEventListener('submit', function(e) {
        // Check P.IVA/CF requirement
        if (!checkPivaCfRequired()) {
            e.preventDefault();
            alert('È obbligatorio inserire almeno uno tra Partita IVA e Codice Fiscale');
            return;
        }
        
        // Check other required fields
        const allTabs = document.querySelectorAll('.tab-pane');
        let allValid = true;
        
        allTabs.forEach(tab => {
            const inputs = tab.querySelectorAll('input[required], select[required], textarea[required]');
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    allValid = false;
                    input.classList.add('is-invalid');
                } else {
                    input.classList.remove('is-invalid');
                }
            });
        });
        
        if (!allValid) {
            e.preventDefault();
            alert('Compila tutti i campi obbligatori prima di salvare.');
        }
    });
    
    // Remove invalid class on input
    document.querySelectorAll('input, select, textarea').forEach(input => {
        input.addEventListener('input', function() {
            this.classList.remove('is-invalid');
        });
    });
});
</script>
{% endblock %}
```


### elenco.html

```html
{% extends 'base.html' %}
{% load static %}

{% block title %}Elenco Clienti{% endblock %}

{% block extra_css %}
<style>
    .table-responsive {
        border-radius: 0.5rem;
        overflow: hidden;
    }
    .search-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .stats-bar {
        background: white;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .client-badge {
        font-size: 0.8rem;
        padding: 0.4rem 0.8rem;
    }
    .action-buttons .btn {
        margin-right: 0.2rem;
        margin-bottom: 0.5rem;
    }
    .rappresentante-chip {
        background: linear-gradient(45deg, #3498db, #2ecc71);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        text-decoration: none;
        display: inline-block;
    }
    .rappresentante-chip:hover {
        color: white;
        transform: scale(1.05);
        transition: all 0.2s ease;
    }
    .client-card {
        border: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        border-radius: 10px;
    }
    .client-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    .client-avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(45deg, #667eea, #764ba2);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 1.2rem;
    }
</style>
{% endblock %}

{% block content %}
<div class="container-fluid">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h1 class="h3 mb-0 text-gray-800">Elenco Clienti</h1>
            <p class="text-muted">Gestione clienti aziendali</p>
        </div>
        <div class="btn-group" role="group">
            <a href="{% url 'anagrafica:nuovo_cliente' %}" class="btn btn-primary">
                <i class="fas fa-plus"></i> Nuovo Cliente
            </a>
            <button type="button" class="btn btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown">
                <i class="fas fa-cog"></i> Azioni
            </button>
            <ul class="dropdown-menu">
                <li><a class="dropdown-item" href="{% url 'anagrafica:export_anagrafica' %}?tipo=clienti">
                    <i class="fas fa-download"></i> Esporta CSV
                </a></li>
                <li><a class="dropdown-item" href="{% url 'anagrafica:clienti_pdf' %}">
                    <i class="fas fa-file-pdf"></i> Report PDF
                </a></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item" href="#" onclick="importClienti()">
                    <i class="fas fa-upload"></i> Importa Clienti
                </a></li>
            </ul>
        </div>
    </div>

    <!-- Search/Filter Section -->
    <div class="search-box">
        <form method="get" class="row g-3">
            <div class="col-md-4">
                <label for="search" class="form-label">Cerca</label>
                <div class="input-group">
                    <span class="input-group-text"><i class="fas fa-search"></i></span>
                    <input type="text" class="form-control" id="search" name="search" 
                           value="{{ request.GET.search }}" placeholder="Ragione sociale, email, telefono...">
                </div>
            </div>
            <div class="col-md-3">
                <label for="rappresentante" class="form-label">Rappresentante</label>
                <select class="form-select" id="rappresentante" name="rappresentante">
                    <option value="">Tutti i rappresentanti</option>
                    {% for rappresentante_item in rappresentanti %}
                    <option value="{{ rappresentante_item.id }}" 
                            {% if request.GET.rappresentante == rappresentante_item.id|stringformat:"s" %}selected{% endif %}>
                        {{ rappresentante_item.nome }}
                    </option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-2">
                <label for="attivo" class="form-label">Stato</label>
                <select class="form-select" id="attivo" name="attivo">
                    <option value="True" {% if request.GET.attivo != 'False' %}selected{% endif %}>Attivi</option>
                    <option value="False" {% if request.GET.attivo == 'False' %}selected{% endif %}>Non attivi</option>
                </select>
            </div>
            <div class="col-md-2">
                <label for="pagamento" class="form-label">Pagamento</label>
                <select class="form-select" id="pagamento" name="pagamento">
                    <option value="">Tutti</option>
                    <option value="01" {% if request.GET.pagamento == '01' %}selected{% endif %}>Immediato</option>
                    <option value="30" {% if request.GET.pagamento == '30' %}selected{% endif %}>30 gg</option>
                    <option value="60" {% if request.GET.pagamento == '60' %}selected{% endif %}>60 gg</option>
                    <option value="90" {% if request.GET.pagamento == '90' %}selected{% endif %}>90 gg</option>
                </select>
            </div>
            <div class="col-md-1 d-flex align-items-end">
                <button type="submit" class="btn btn-primary w-100">
                    <i class="fas fa-search"></i>
                </button>
            </div>
        </form>
    </div>

    <!-- Statistics Bar -->
    <div class="stats-bar">
        <div class="row text-center">
            <div class="col-md-3">
                <div class="d-flex align-items-center justify-content-center">
                    <i class="fas fa-building fa-2x text-primary me-3"></i>
                    <div>
                        <h4 class="mb-0">{{ total_count }}</h4>
                        <small class="text-muted">Clienti Totali</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="d-flex align-items-center justify-content-center">
                    <i class="fas fa-check-circle fa-2x text-success me-3"></i>
                    <div>
                        <h4 class="mb-0">{{ clienti.filter:attivo:True|length }}</h4>
                        <small class="text-muted">Attivi</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="d-flex align-items-center justify-content-center">
                    <i class="fas fa-calendar fa-2x text-info me-3"></i>
                    <div>
                        <h4 class="mb-0">{{ clienti.filter:data_creazione__date:today|length|default:0 }}</h4>
                        <small class="text-muted">Oggi</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="d-flex align-items-center justify-content-center">
                    <i class="fas fa-user-tie fa-2x text-warning me-3"></i>
                    <div>
                        <h4 class="mb-0">{{ rappresentanti.count }}</h4>
                        <small class="text-muted">Rappresentanti</small>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bulk Actions Bar -->
    <div class="d-none" id="bulk-actions-bar">
        <div class="alert alert-info d-flex justify-content-between align-items-center">
            <div>
                <i class="fas fa-info-circle me-2"></i>
                <span id="selected-count">0</span> clienti selezionati
            </div>
            <div>
                <button class="btn btn-sm btn-warning me-2" onclick="bulkActivate()">
                    <i class="fas fa-check"></i> Attiva
                </button>
                <button class="btn btn-sm btn-secondary me-2" onclick="bulkDeactivate()">
                    <i class="fas fa-times"></i> Disattiva
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="clearSelection()">
                    <i class="fas fa-undo"></i> Deseleziona
                </button>
            </div>
        </div>
    </div>

    <!-- Table -->
    <div class="card client-card">
        <div class="card-body p-0">
            <div class="table-responsive">
                <table class="table table-hover mb-0">
                    <thead class="table-light">
                        <tr>
                            <th style="width: 50px;">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="selectAll">
                                </div>
                            </th>
                            <th>Cliente</th>
                            <th>Rappresentante</th>
                            <th>Contatti</th>
                            <th>Ubicazione</th>
                            <th>Condizioni</th>
                            <th>Stato</th>
                            <th style="width: 120px;">Azioni</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for cliente in clienti %}
                        <tr>
                            <td>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" value="{{ cliente.id }}" 
                                           name="selected_items">
                                </div>
                            </td>
                            <td>
                                <div class="d-flex align-items-center">
                                    <div class="client-avatar me-3">
                                        {{ cliente.ragione_sociale|first|upper }}
                                    </div>
                                    <div>
                                        <strong>{{ cliente.ragione_sociale }}</strong>
                                        <br>
                                        <small class="text-muted">
                                            {% if cliente.partita_iva %}P.IVA: {{ cliente.partita_iva }}{% endif %}
                                            {% if cliente.codice_fiscale and cliente.partita_iva %} | {% endif %}
                                            {% if cliente.codice_fiscale %}CF: {{ cliente.codice_fiscale|slice:":16" }}{% endif %}
                                        </small>
                                    </div>
                                </div>
                            </td>
                            <td>
                                {% if cliente.rappresentante %}
                                <a href="{% url 'anagrafica:dettaglio_rappresentante' cliente.rappresentante.pk %}" 
                                   class="rappresentante-chip">
                                    <i class="fas fa-user-tie"></i> {{ cliente.rappresentante.nome }}
                                </a>
                                {% else %}
                                <span class="badge bg-light text-muted">Nessun rappresentante</span>
                                {% endif %}
                            </td>
                            <td>
                                <div>
                                    <i class="fas fa-envelope text-muted me-1"></i>
                                    <a href="mailto:{{ cliente.email }}" class="text-decoration-none">
                                        {{ cliente.email|truncatechars:25 }}
                                    </a>
                                </div>
                                <div class="mt-1">
                                    <i class="fas fa-phone text-muted me-1"></i>
                                    <a href="tel:{{ cliente.telefono }}" class="text-decoration-none">
                                        {{ cliente.telefono }}
                                    </a>
                                </div>
                            </td>
                            <td>
                                <div>
                                    <i class="fas fa-map-marker-alt text-muted me-1"></i>
                                    {{ cliente.città }} ({{ cliente.provincia }})
                                </div>
                                <div class="mt-1">
                                    <small class="text-muted">{{ cliente.indirizzo|truncatechars:30 }}</small>
                                </div>
                            </td>
                            <td>
                                <div>
                                    <span class="badge client-badge" 
                                          style="background-color: {% if cliente.pagamento == '01' %}#e74c3c{% elif cliente.pagamento == '30' %}#f39c12{% elif cliente.pagamento == '60' %}#3498db{% else %}#9b59b6{% endif %}; color: white;">
                                        {{ cliente.get_pagamento_display }}
                                    </span>
                                </div>
                                {% if cliente.limite_credito %}
                                <div class="mt-1">
                                    <small class="text-muted">
                                        <i class="fas fa-euro-sign"></i> {{ cliente.limite_credito|floatformat:0 }}
                                    </small>
                                </div>
                                {% endif %}
                                {% if cliente.sconto_percentuale %}
                                <div class="mt-1">
                                    <small class="text-success">
                                        <i class="fas fa-percentage"></i> {{ cliente.sconto_percentuale }}%
                                    </small>
                                </div>
                                {% endif %}
                            </td>
                            <td>
                                {% if cliente.attivo %}
                                <span class="badge bg-success">
                                    <i class="fas fa-check"></i> Attivo
                                </span>
                                {% else %}
                                <span class="badge bg-danger">
                                    <i class="fas fa-times"></i> Non attivo
                                </span>
                                {% endif %}
                            </td>
                            <td>
                                <div class="action-buttons">
                                    <a href="{% url 'anagrafica:dettaglio_cliente' cliente.pk %}" 
                                       class="btn btn-sm btn-outline-primary" title="Visualizza">
                                        <i class="fas fa-eye"></i>
                                    </a>
                                    <a href="{% url 'anagrafica:modifica_cliente' cliente.pk %}" 
                                       class="btn btn-sm btn-outline-secondary" title="Modifica">
                                        <i class="fas fa-edit"></i>
                                    </a>
                                    <button type="button" class="btn btn-sm btn-outline-warning" 
                                            onclick="toggleActive({{ cliente.pk }}, {{ cliente.attivo|yesno:'false,true' }})"
                                            title="{% if cliente.attivo %}Disattiva{% else %}Attiva{% endif %}">
                                        <i class="fas fa-toggle-{% if cliente.attivo %}on{% else %}off{% endif %}"></i>
                                    </button>
                                    <a href="{% url 'anagrafica:elimina_cliente' cliente.pk %}" 
                                       class="btn btn-sm btn-outline-danger" title="Elimina"
                                       onclick="return confirm('Sei sicuro di voler eliminare questo cliente?')">
                                        <i class="fas fa-trash"></i>
                                    </a>
                                </div>
                            </td>
                        </tr>
                        {% empty %}
                        <tr>
                            <td colspan="8" class="text-center py-5 text-muted">
                                <i class="fas fa-inbox fa-3x mb-3"></i>
                                <br>
                                {% if request.GET.search %}
                                Nessun cliente trovato con i criteri specificati.
                                <br>
                                <a href="{% url 'anagrafica:elenco_clienti' %}" class="btn btn-sm btn-outline-primary mt-2">
                                    <i class="fas fa-undo"></i> Rimuovi filtri
                                </a>
                                {% else %}
                                Nessun cliente presente.
                                <br>
                                <a href="{% url 'anagrafica:nuovo_cliente' %}" class="btn btn-sm btn-primary mt-2">
                                    <i class="fas fa-plus"></i> Aggiungi primo cliente
                                </a>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Pagination -->
    {% if is_paginated %}
    <nav aria-label="Page navigation" class="mt-4">
        <ul class="pagination justify-content-center">
            {% if page_obj.has_previous %}
            <li class="page-item">
                <a class="page-link" href="?{% for key, value in request.GET.items %}{% if key != 'page' %}{{ key }}={{ value }}&{% endif %}{% endfor %}page=1">
                    <i class="fas fa-angle-double-left"></i>
                </a>
            </li>
            <li class="page-item">
                <a class="page-link" href="?{% for key, value in request.GET.items %}{% if key != 'page' %}{{ key }}={{ value }}&{% endif %}{% endfor %}page={{ page_obj.previous_page_number }}">
                    <i class="fas fa-angle-left"></i>
                </a>
            </li>
            {% endif %}
            
            {% for num in page_obj.paginator.page_range %}
                {% if page_obj.number == num %}
                <li class="page-item active">
                    <span class="page-link">{{ num }}</span>
                </li>
                {% elif num > page_obj.number|add:'-3' and num < page_obj.number|add:'3' %}
                <li class="page-item">
                    <a class="page-link" href="?{% for key, value in request.GET.items %}{% if key != 'page' %}{{ key }}={{ value }}&{% endif %}{% endfor %}page={{ num }}">{{ num }}</a>
                </li>
                {% endif %}
            {% endfor %}
            
            {% if page_obj.has_next %}
            <li class="page-item">
                <a class="page-link" href="?{% for key, value in request.GET.items %}{% if key != 'page' %}{{ key }}={{ value }}&{% endif %}{% endfor %}page={{ page_obj.next_page_number }}">
                    <i class="fas fa-angle-right"></i>
                </a>
            </li>
            <li class="page-item">
                <a class="page-link" href="?{% for key, value in request.GET.items %}{% if key != 'page' %}{{ key }}={{ value }}&{% endif %}{% endfor %}page={{ page_obj.paginator.num_pages }}">
                    <i class="fas fa-angle-double-right"></i>
                </a>
            </li>
            {% endif %}
        </ul>
    </nav>
    {% endif %}
</div>
{% endblock %}

{% block extra_js %}
<script>
// Select all functionality
function updateBulkActions() {
    const checkboxes = document.querySelectorAll('input[name="selected_items"]');
    const selected = document.querySelectorAll('input[name="selected_items"]:checked');
    const bulkBar = document.getElementById('bulk-actions-bar');
    const selectedCount = document.getElementById('selected-count');
    
    selectedCount.textContent = selected.length;
    
    if (selected.length > 0) {
        bulkBar.classList.remove('d-none');
    } else {
        bulkBar.classList.add('d-none');
    }
}

document.getElementById('selectAll').addEventListener('change', function() {
    const checkboxes = document.querySelectorAll('input[name="selected_items"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = this.checked;
    });
    updateBulkActions();
});

document.querySelectorAll('input[name="selected_items"]').forEach(checkbox => {
    checkbox.addEventListener('change', updateBulkActions);
});

// Toggle active/inactive status
function toggleActive(id, newStatus) {
    if (confirm('Sei sicuro di voler ' + (newStatus ? 'attivare' : 'disattivare') + ' questo cliente?')) {
        fetch(`{% url 'anagrafica:toggle_attivo' 'cliente' 0 %}`.replace('0', id), {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json',
            },
        }).then(response => {
            if (response.ok) {
                location.reload();
            } else {
                alert('Errore durante l\'operazione');
            }
        });
    }
}

// Bulk operations
function bulkActivate() {
    const selected = document.querySelectorAll('input[name="selected_items"]:checked');
    const ids = Array.from(selected).map(checkbox => checkbox.value);
    
    if (ids.length === 0) {
        alert('Seleziona almeno un cliente');
        return;
    }
    
    if (confirm(`Attivare ${ids.length} clienti selezionati?`)) {
        fetch('{% url "anagrafica:attiva_multipli" %}', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                'tipo': 'cliente',
                'ids': ids
            })
        }).then(response => {
            if (response.ok) {
                location.reload();
            }
        });
    }
}

function bulkDeactivate() {
    const selected = document.querySelectorAll('input[name="selected_items"]:checked');
    const ids = Array.from(selected).map(checkbox => checkbox.value);
    
    if (ids.length === 0) {
        alert('Seleziona almeno un cliente');
        return;
    }
    
    if (confirm(`Disattivare ${ids.length} clienti selezionati?`)) {
        fetch('{% url "anagrafica:disattiva_multipli" %}', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                'tipo': 'cliente',
                'ids': ids
            })
        }).then(response => {
            if (response.ok) {
                location.reload();
            }
        });
    }
}

function clearSelection() {
    document.getElementById('selectAll').checked = false;
    document.querySelectorAll('input[name="selected_items"]').forEach(checkbox => {
        checkbox.checked = false;
    });
    updateBulkActions();
}

function importClienti() {
    window.location.href = '{% url "anagrafica:import_clienti" %}';
}
</script>
{% endblock %}
```


### dettaglio.html

```html
{% extends 'base.html' %}
{% load static %}

{% block title %}{{ cliente.ragione_sociale }} - Dettagli{% endblock %}

{% block extra_css %}
<style>
    .profile-card {
        background: linear-gradient(135deg, #2ecc71 0%, #3498db 100%);
        color: white;
        border-radius: 15px;
        padding: 2rem;
        margin-bottom: 2rem;
    }
    .info-card {
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    .info-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    .info-label {
        font-weight: 600;
        color: #6c757d;
        font-size: 0.9rem;
    }
    .info-value {
        font-size: 1.1rem;
        color: #495057;
    }
    .metric-card {
        text-align: center;
        padding: 1.5rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
    }
    .metric-number {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .quick-actions .btn {
        margin: 0.25rem;
    }
    .rappresentante-badge {
        background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        text-decoration: none;
        display: inline-block;
        font-weight: 500;
    }
    .rappresentante-badge:hover {
        color: white;
        transform: scale(1.05);
        transition: all 0.2s ease;
    }
    .status-indicator {
        position: relative;
        display: inline-block;
    }
    .status-indicator::before {
        content: '';
        position: absolute;
        top: 50%;
        left: -15px;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        transform: translateY(-50%);
    }
    .status-indicator.active::before {
        background-color: #27ae60;
        animation: pulse 2s infinite;
    }
    .status-indicator.inactive::before {
        background-color: #e74c3c;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    .document-item {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #007bff;
    }
    .activity-timeline {
        position: relative;
        padding-left: 30px;
    }
    .activity-timeline::before {
        content: '';
        position: absolute;
        left: 15px;
        top: 0;
        bottom: 0;
        width: 2px;
        background: #dee2e6;
    }
    .activity-item {
        position: relative;
        margin-bottom: 1.5rem;
    }
    .activity-item::before {
        content: '';
        position: absolute;
        left: -7px;
        top: 8px;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: #007bff;
        border: 2px solid white;
    }
</style>
{% endblock %}

{% block content %}
<div class="container-fluid">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="{% url 'anagrafica:dashboard' %}">Anagrafica</a></li>
                    <li class="breadcrumb-item"><a href="{% url 'anagrafica:elenco_clienti' %}">Clienti</a></li>
                    <li class="breadcrumb-item active">{{ cliente.ragione_sociale|truncatechars:30 }}</li>
                </ol>
            </nav>
            <h1 class="h3 mb-0">Dettagli Cliente</h1>
        </div>
        <div class="quick-actions">
            <a href="{% url 'anagrafica:modifica_cliente' cliente.pk %}" class="btn btn-primary">
                <i class="fas fa-edit"></i> Modifica
            </a>
            <button class="btn btn-warning" onclick="toggleStatus('{{ cliente.pk }}', '{{ cliente.attivo|yesno:'false,true' }}')">
                <i class="fas fa-toggle-{% if cliente.attivo %}on{% else %}off{% endif %}"></i>
                {% if cliente.attivo %}Disattiva{% else %}Attiva{% endif %}
            </button>
            <button class="btn btn-success" onclick="sendEmail('{{ cliente.email }}')">
                <i class="fas fa-envelope"></i> Email
            </button>
            <div class="btn-group" role="group">
                <button class="btn btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                    <i class="fas fa-cog"></i> Azioni
                </button>
                <ul class="dropdown-menu">
                    <li><a class="dropdown-item" href="tel:{{ cliente.telefono }}">
                        <i class="fas fa-phone"></i> Chiama
                    </a></li>
                    <li><hr class="dropdown-divider"></li>
                    <li><a class="dropdown-item" href="#" onclick="exportCliente()">
                        <i class="fas fa-download"></i> Esporta Dati
                    </a></li>
                    <li><a class="dropdown-item" href="#" onclick="duplicateCliente()">
                        <i class="fas fa-copy"></i> Duplica Cliente
                    </a></li>
                    <li><hr class="dropdown-divider"></li>
                    <li><a class="dropdown-item text-danger" href="{% url 'anagrafica:elimina_cliente' cliente.pk %}">
                        <i class="fas fa-trash"></i> Elimina
                    </a></li>
                </ul>
            </div>
        </div>
    </div>

    <!-- Profile Card -->
    <div class="profile-card">
        <div class="row align-items-center">
            <div class="col-md-2 text-center">
                <div class="avatar-large">
                    <div class="rounded-circle bg-white d-flex align-items-center justify-content-center mx-auto" 
                         style="width: 100px; height: 100px;">
                        <i class="fas fa-building fa-3x text-primary"></i>
                    </div>
                </div>
            </div>
            <div class="col-md-7">
                <h2 class="mb-3">{{ cliente.ragione_sociale }}</h2>
                <div class="row">
                    <div class="col-md-6">
                        <p class="mb-2"><i class="fas fa-envelope me-2"></i> {{ cliente.email }}</p>
                        <p class="mb-2"><i class="fas fa-phone me-2"></i> {{ cliente.telefono }}</p>
                        <p class="mb-2"><i class="fas fa-map-marker-alt me-2"></i> {{ cliente.città }}, {{ cliente.provincia }}</p>
                    </div>
                    <div class="col-md-6">
                        {% if cliente.rappresentante %}
                        <p class="mb-2">
                            <i class="fas fa-user-tie me-2"></i>
                            <a href="{% url 'anagrafica:dettaglio_rappresentante' cliente.rappresentante.pk %}" 
                               class="rappresentante-badge">
                                {{ cliente.rappresentante.nome }}
                            </a>
                        </p>
                        {% endif %}
                        <p class="mb-2">
                            <i class="fas fa-calendar me-2"></i> 
                            Cliente dal {{ cliente.data_creazione|date:"d/m/Y" }}
                        </p>
                        <p class="mb-0">
                            <i class="fas fa-circle me-2"></i>
                            <span class="status-indicator {% if cliente.attivo %}active{% else %}inactive{% endif %}">
                                Stato: {% if cliente.attivo %}Attivo{% else %}Non Attivo{% endif %}
                            </span>
                        </p>
                    </div>
                </div>
            </div>
            <div class="col-md-3 text-center">
                <div class="bg-white bg-opacity-20 rounded p-3">
                    <div class="metric-number" style="color: white; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        €{{ 0|floatformat:0 }}
                    </div>
                    <div class="metric-label">Fatturato Totale</div>
                </div>
            </div>
        </div>
    </div>

    <!-- Metrics Cards -->
    <div class="row mb-4">
        <div class="col-md-3">
            <div class="card metric-card">
                <div class="metric-number">{{ 0 }}</div>
                <div class="metric-label">Ordini Totali</div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card metric-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
                <div class="metric-number">€{{ cliente.limite_credito|default:0|floatformat:0 }}</div>
                <div class="metric-label">Limite Credito</div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card metric-card" style="background: linear-gradient(135deg, #7b68ee 0%, #9d50bb 100%);">
                <div class="metric-number">{{ cliente.sconto_percentuale|default:0 }}%</div>
                <div class="metric-label">Sconto Applicato</div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card metric-card" style="background: linear-gradient(135deg, #ff9a56 0%, #ffad56 100%);">
                <div class="metric-number">{{ cliente.pagamento|slice:":2" }} gg</div>
                <div class="metric-label">Giorni Pagamento</div>
            </div>
        </div>
    </div>

    <!-- Information Sections -->
    <div class="row">
        <!-- Informazioni Anagrafiche -->
        <div class="col-md-6">
            <div class="card info-card">
                <div class="card-header bg-primary text-white">
                    <h5 class="card-title mb-0">
                        <i class="fas fa-id-card me-2"></i>
                        Informazioni Anagrafiche
                    </h5>
                </div>
                <div class="card-body">
                    <div class="row mb-3">
                        <div class="col-sm-4 info-label">Ragione Sociale:</div>
                        <div class="col-sm-8 info-value">{{ cliente.ragione_sociale }}</div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-sm-4 info-label">Indirizzo:</div>
                        <div class="col-sm-8 info-value">
                            {{ cliente.indirizzo }}<br>
                            {{ cliente.cap }} {{ cliente.città }} ({{ cliente.provincia }})
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-sm-4 info-label">Partita IVA:</div>
                        <div class="col-sm-8 info-value">
                            {% if cliente.partita_iva %}
                                {{ cliente.partita_iva }}
                                <span class="badge bg-success ms-2">Verificata</span>
                            {% else %}
                                <span class="text-muted">Non presente</span>
                            {% endif %}
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-sm-4 info-label">Codice Fiscale:</div>
                        <div class="col-sm-8 info-value">{{ cliente.codice_fiscale }}</div>
                    </div>
                    <div class="row mb-0">
                        <div class="col-sm-4 info-label">Codice Univoco:</div>
                        <div class="col-sm-8 info-value">{{ cliente.codice_univoco|default:"Non specificato" }}</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Condizioni Commerciali -->
        <div class="col-md-6">
            <div class="card info-card">
                <div class="card-header bg-success text-white">
                    <h5 class="card-title mb-0">
                        <i class="fas fa-handshake me-2"></i>
                        Condizioni Commerciali
                    </h5>
                </div>
                <div class="card-body">
                    <div class="row mb-3">
                        <div class="col-sm-4 info-label">Modalità Pagamento:</div>
                        <div class="col-sm-8 info-value">
                            <span class="badge" 
                                  style="background-color: {% if cliente.pagamento == '01' %}#e74c3c{% elif cliente.pagamento == '30' %}#f39c12{% elif cliente.pagamento == '60' %}#3498db{% else %}#9b59b6{% endif %}; color: white; font-size: 0.9rem;">
                                {{ cliente.get_pagamento_display }}
                            </span>
                        </div>
                    </div>
                    {% if cliente.limite_credito %}
                    <div class="row mb-3">
                        <div class="col-sm-4 info-label">Limite Credito:</div>
                        <div class="col-sm-8 info-value">
                            €{{ cliente.limite_credito|floatformat:2 }}
                            <i class="fas fa-euro-sign text-success"></i>
                        </div>
                    </div>
                    {% endif %}
                    {% if cliente.sconto_percentuale %}
                    <div class="row mb-3">
                        <div class="col-sm-4 info-label">Sconto Percentuale:</div>
                        <div class="col-sm-8 info-value">
                            {{ cliente.sconto_percentuale }}%
                            <i class="fas fa-percentage text-info"></i>
                        </div>
                    </div>
                    {% endif %}
                    <div class="row mb-3">
                        <div class="col-sm-4 info-label">Zona:</div>
                        <div class="col-sm-8 info-value">{{ cliente.zona|default:"Non specificata" }}</div>
                    </div>
                    <div class="row mb-0">
                        <div class="col-sm-4 info-label">Rappresentante:</div>
                        <div class="col-sm-8 info-value">
                            {% if cliente.rappresentante %}
                                <a href="{% url 'anagrafica:dettaglio_rappresentante' cliente.rappresentante.pk %}" 
                                   class="text-decoration-none">
                                    {{ cliente.rappresentante.nome }}
                                    <i class="fas fa-external-link-alt ms-1"></i>
                                </a>
                            {% else %}
                                <span class="text-muted">Nessun rappresentante assegnato</span>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Note del Cliente -->
    {% if cliente.note %}
    <div class="row mt-4">
        <div class="col-12">
            <div class="card info-card">
                <div class="card-header bg-info text-white">
                    <h5 class="card-title mb-0">
                        <i class="fas fa-sticky-note me-2"></i>
                        Note Aggiuntive
                    </h5>
                </div>
                <div class="card-body">
                    {{ cliente.note|linebreaks }}
                </div>
            </div>
        </div>
    </div>
    {% endif %}

    <!-- Attività Recenti -->
    <div class="row mt-4">
        <div class="col-12">
            <div class="card info-card">
                <div class="card-header bg-warning text-white">
                    <h5 class="card-title mb-0">
                        <i class="fas fa-history me-2"></i>
                        Attività Recenti
                    </h5>
                </div>
                <div class="card-body">
                    <div class="activity-timeline">
                        <div class="activity-item">
                            <div class="d-flex justify-content-between">
                                <div>
                                    <strong>Cliente creato</strong>
                                    <p class="mb-0 text-muted">
                                        Cliente aggiunto al sistema
                                        {% if cliente.rappresentante %}da {{ cliente.rappresentante.nome }}{% endif %}
                                    </p>
                                </div>
                                <span class="text-muted">{{ cliente.data_creazione|date:"d/m/Y H:i" }}</span>
                            </div>
                        </div>
                        <div class="activity-item">
                            <div class="d-flex justify-content-between">
                                <div>
                                    <strong>Ultima modifica</strong>
                                    <p class="mb-0 text-muted">Dati cliente aggiornati</p>
                                </div>
                                <span class="text-muted">{{ cliente.data_modifica|date:"d/m/Y H:i" }}</span>
                            </div>
                        </div>
                        <!-- Qui andrebbero altre attività future (ordini, fatture, ecc.) -->
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Documenti/Allegati (Placeholder per future implementazioni) -->
    <div class="row mt-4">
        <div class="col-12">
            <div class="card info-card">
                <div class="card-header bg-secondary text-white">
                    <h5 class="card-title mb-0">
                        <i class="fas fa-folder me-2"></i>
                        Documenti Allegati
                    </h5>
                </div>
                <div class="card-body">
                    <div class="alert alert-light text-center" role="alert">
                        <i class="fas fa-file-alt fa-2x text-muted mb-3"></i>
                        <p class="mb-0">Nessun documento allegato</p>
                        <button class="btn btn-outline-primary btn-sm mt-2">
                            <i class="fas fa-upload"></i> Aggiungi Documento
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
function toggleStatus(id, newStatus) {
    if (confirm('Sei sicuro di voler ' + (newStatus === 'true' ? 'attivare' : 'disattivare') + ' questo cliente?')) {
        fetch(`{% url 'anagrafica:toggle_attivo' 'cliente' 0 %}`.replace('0', id), {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json',
            },
        }).then(response => {
            if (response.ok) {
                location.reload();
            } else {
                alert('Errore durante l\'operazione');
            }
        });
    }
}

function sendEmail(email) {
    window.location.href = `mailto:${email}`;
}

function exportCliente() {
    const exportUrl = `{% url 'anagrafica:export_anagrafica' %}?tipo=cliente&id={{ cliente.pk }}`;
    window.open(exportUrl, '_blank');
}

function duplicateCliente() {
    if (confirm('Creare una copia di questo cliente?')) {
        // Implementare la logica di duplicazione
        alert('Funzionalità in sviluppo');
    }
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
</script>
{% endblock %}
```


### nuovo.html

```html
{% extends 'base.html' %}
{% load static %}
{% load crispy_forms_tags %}

{% block title %}
{% if view.object.pk %}Modifica Rappresentante{% else %}Nuovo Rappresentante{% endif %}
{% endblock %}

{% block extra_css %}
<style>
    .form-container {
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        padding: 2rem;
        margin-top: 1rem;
    }
    
    .step-indicator {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .navbar {
        margin-bottom: 0;
    }
    
    .tab-content {
        padding: 1.5rem 0;
        border-top: 2px solid #e9ecef;
    }
    
    .nav-tabs {
        background-color: #f8f9fa;
        border-radius: 8px 8px 0 0;
        padding: 0.5rem;
    }
    
    .nav-tabs .nav-link {
        border: none;
        border-radius: 25px;
        margin-right: 0.5rem;
        padding: 0.75rem 1.5rem;
        color: #667eea;
        font-weight: 500;
        transition: all 0.3s ease;
        background-color: transparent;
    }
    
    .nav-tabs .nav-link:hover {
        background-color: rgba(102, 126, 234, 0.1);
        color: #5a6ab8;
    }
    
    .nav-tabs .nav-link.active {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: transparent;
    }
    
    .form-label {
        color: #495057;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .form-control, .form-select {
        border: 2px solid #e9ecef;
        border-radius: 8px;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .form-control:focus, .form-select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
    }
    
    .btn-primary {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    .btn-secondary {
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
    }
    
    .required-field::after {
        content: ' *';
        color: #dc3545;
    }
    
    .field-help {
        font-size: 0.875rem;
        color: #6c757d;
        margin-top: 0.25rem;
    }
    
    .validation-message {
        background-color: #f8f9fa;
        border: 1px solid #e2e2e8;
        border-radius: 8px;
        padding: 0.75rem;
        margin-top: 0.5rem;
        font-size: 0.875rem;
    }
    
    .validation-message.valid {
        border-color: #28a745;
        color: #155724;
        background-color: #d4edda;
    }
    
    .validation-message.invalid {
        border-color: #dc3545;
        color: #721c24;
        background-color: #f8d7da;
    }
    
    .tab-pane {
        background-color: white;
        border-radius: 0 0 8px 8px;
        border: 1px solid #e9ecef;
        border-top: none;
        padding: 1.5rem;
    }
</style>
{% endblock %}

{% block content %}
<div class="container-fluid">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="{% url 'anagrafica:dashboard' %}">Anagrafica</a></li>
                    <li class="breadcrumb-item"><a href="{% url 'anagrafica:elenco_rappresentanti' %}">Rappresentanti</a></li>
                    <li class="breadcrumb-item active">
                        {% if view.object.pk %}Modifica{% else %}Nuovo{% endif %}
                    </li>
                </ol>
            </nav>
            <h1 class="h3 mb-0">
                {% if view.object.pk %}
                    <i class="fas fa-edit"></i> Modifica Rappresentante
                {% else %}
                    <i class="fas fa-plus"></i> Nuovo Rappresentante
                {% endif %}
            </h1>
        </div>
    </div>

    <!-- Step Indicator -->
    <div class="step-indicator">
        <h4 class="mb-0">
            {% if view.object.pk %}
                Modifica i dati del rappresentante {{ view.object.nome }}
            {% else %}
                Inserimento nuovo rappresentante
            {% endif %}
        </h4>
        <p class="mb-0 mt-2 opacity-75">
            Completa tutti i campi obbligatori per salvare il rappresentante
        </p>
    </div>

    <!-- Form Container -->
    <div class="form-container">
        <form method="post" id="rappresentanteForm">
            {% csrf_token %}
            
            <!-- Form Errors (if any) -->
            {% if form.non_field_errors %}
            <div class="alert alert-danger" role="alert">
                <h5 class="alert-heading"><i class="fas fa-exclamation-triangle"></i> Errori di validazione</h5>
                {% for error in form.non_field_errors %}
                    <p class="mb-0">{{ error }}</p>
                {% endfor %}
            </div>
            {% endif %}
            
            <!-- Tabs Navigation -->
            <ul class="nav nav-tabs" id="formTabs" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="general-tab" data-bs-toggle="tab" 
                            data-bs-target="#general" type="button" role="tab">
                        <i class="fas fa-user-circle"></i> Informazioni Generali
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="fiscal-tab" data-bs-toggle="tab" 
                            data-bs-target="#fiscal" type="button" role="tab">
                        <i class="fas fa-id-card"></i> Dati Fiscali
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="commercial-tab" data-bs-toggle="tab" 
                            data-bs-target="#commercial" type="button" role="tab">
                        <i class="fas fa-handshake"></i> Dati Commerciali
                    </button>
                </li>
            </ul>
            
            <!-- Tab Content -->
            <div class="tab-content" id="formTabContent">
                <!-- Tab 1: Informazioni Generali -->
                <div class="tab-pane fade show active" id="general" role="tabpanel">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.user.id_for_label }}" class="form-label">
                                    <i class="fas fa-user me-2"></i>Utente Associato
                                </label>
                                {{ form.user|add_class:"form-select" }}
                                {% if form.user.errors %}
                                    <div class="invalid-feedback d-block">{{ form.user.errors|join:', ' }}</div>
                                {% endif %}
                                <div class="field-help">Seleziona l'utente dipendente da associare al rappresentante</div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.nome.id_for_label }}" class="form-label required-field">
                                    <i class="fas fa-signature me-2"></i>Nome Completo
                                </label>
                                {{ form.nome|add_class:"form-control" }}
                                {% if form.nome.errors %}
                                    <div class="invalid-feedback d-block">{{ form.nome.errors|join:', ' }}</div>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-12">
                            <div class="mb-3">
                                <label for="{{ form.ragione_sociale.id_for_label }}" class="form-label required-field">
                                    <i class="fas fa-building me-2"></i>Ragione Sociale
                                </label>
                                {{ form.ragione_sociale|add_class:"form-control" }}
                                {% if form.ragione_sociale.errors %}
                                    <div class="invalid-feedback d-block">{{ form.ragione_sociale.errors|join:', ' }}</div>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-8">
                            <div class="mb-3">
                                <label for="{{ form.indirizzo.id_for_label }}" class="form-label">
                                    <i class="fas fa-map-marker-alt me-2"></i>Indirizzo
                                </label>
                                {{ form.indirizzo|add_class:"form-control" }}
                                {% if form.indirizzo.errors %}
                                    <div class="invalid-feedback d-block">{{ form.indirizzo.errors|join:', ' }}</div>
                                {% endif %}
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="mb-3">
                                <label for="{{ form.cap.id_for_label }}" class="form-label">
                                    CAP
                                </label>
                                {{ form.cap|add_class:"form-control" }}
                                {% if form.cap.errors %}
                                    <div class="invalid-feedback d-block">{{ form.cap.errors|join:', ' }}</div>
                                {% endif %}
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="mb-3">
                                <label for="{{ form.provincia.id_for_label }}" class="form-label">
                                    Provincia
                                </label>
                                {{ form.provincia|add_class:"form-control" }}
                                {% if form.provincia.errors %}
                                    <div class="invalid-feedback d-block">{{ form.provincia.errors|join:', ' }}</div>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-8">
                            <div class="mb-3">
                                <label for="{{ form.città.id_for_label }}" class="form-label">
                                    <i class="fas fa-city me-2"></i>Città
                                </label>
                                {{ form.città|add_class:"form-control" }}
                                {% if form.città.errors %}
                                    <div class="invalid-feedback d-block">{{ form.città.errors|join:', ' }}</div>
                                {% endif %}
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="mb-3">
                                <label for="{{ form.zona.id_for_label }}" class="form-label">
                                    <i class="fas fa-globe-europe me-2"></i>Zona di Competenza
                                </label>
                                {{ form.zona|add_class:"form-control" }}
                                {% if form.zona.errors %}
                                    <div class="invalid-feedback d-block">{{ form.zona.errors|join:', ' }}</div>
                                {% endif %}
                                <div class="field-help">Es: Nord Italia, Lombardia, ecc.</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Tab 2: Dati Fiscali -->
                <div class="tab-pane fade" id="fiscal" role="tabpanel">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.partita_iva.id_for_label }}" class="form-label required-field">
                                    <i class="fas fa-file-invoice me-2"></i>Partita IVA
                                </label>
                                {{ form.partita_iva|add_class:"form-control" }}
                                {% if form.partita_iva.errors %}
                                    <div class="invalid-feedback d-block">{{ form.partita_iva.errors|join:', ' }}</div>
                                {% endif %}
                                <div class="validation-message" id="piva-validation" style="display: none;"></div>
                                <div class="field-help">11 cifre numeriche</div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.codice_fiscale.id_for_label }}" class="form-label required-field">
                                    <i class="fas fa-id-badge me-2"></i>Codice Fiscale
                                </label>
                                {{ form.codice_fiscale|add_class:"form-control" }}
                                {% if form.codice_fiscale.errors %}
                                    <div class="invalid-feedback d-block">{{ form.codice_fiscale.errors|join:', ' }}</div>
                                {% endif %}
                                <div class="validation-message" id="cf-validation" style="display: none;"></div>
                                <div class="field-help">16 caratteri per persona fisica o 11 cifre per azienda</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.codice_univoco.id_for_label }}" class="form-label">
                                    <i class="fas fa-qrcode me-2"></i>Codice Univoco
                                </label>
                                {{ form.codice_univoco|add_class:"form-control" }}
                                {% if form.codice_univoco.errors %}
                                    <div class="invalid-feedback d-block">{{ form.codice_univoco.errors|join:', ' }}</div>
                                {% endif %}
                                <div class="field-help">Codice destinatario per fatturazione elettronica</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Tab 3: Dati Commerciali -->
                <div class="tab-pane fade" id="commercial" role="tabpanel">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.telefono.id_for_label }}" class="form-label required-field">
                                    <i class="fas fa-phone me-2"></i>Telefono
                                </label>
                                {{ form.telefono|add_class:"form-control" }}
                                {% if form.telefono.errors %}
                                    <div class="invalid-feedback d-block">{{ form.telefono.errors|join:', ' }}</div>
                                {% endif %}
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.email.id_for_label }}" class="form-label required-field">
                                    <i class="fas fa-envelope me-2"></i>Email
                                </label>
                                {{ form.email|add_class:"form-control" }}
                                {% if form.email.errors %}
                                    <div class="invalid-feedback d-block">{{ form.email.errors|join:', ' }}</div>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.percentuale_sulle_vendite.id_for_label }}" class="form-label required-field">
                                    <i class="fas fa-percentage me-2"></i>Percentuale Provvigioni (%)
                                </label>
                                {{ form.percentuale_sulle_vendite|add_class:"form-control" }}
                                {% if form.percentuale_sulle_vendite.errors %}
                                    <div class="invalid-feedback d-block">{{ form.percentuale_sulle_vendite.errors|join:', ' }}</div>
                                {% endif %}
                                <div class="field-help">Inserire un valore tra 0 e 100</div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3 d-flex align-items-center">
                                <div class="form-check">
                                    {{ form.attivo }}
                                    <label class="form-check-label" for="{{ form.attivo.id_for_label }}">
                                        <i class="fas fa-check-circle me-2"></i>Rappresentante Attivo
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-12">
                            <div class="mb-3">
                                <label for="{{ form.note.id_for_label }}" class="form-label">
                                    <i class="fas fa-sticky-note me-2"></i>Note Aggiuntive
                                </label>
                                {{ form.note|add_class:"form-control" }}
                                {% if form.note.errors %}
                                    <div class="invalid-feedback d-block">{{ form.note.errors|join:', ' }}</div>
                                {% endif %}
                                <div class="field-help">Note interne, non visibili al rappresentante</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Footer Buttons -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="d-flex justify-content-between">
                        <a href="{% url 'anagrafica:elenco_rappresentanti' %}" class="btn btn-secondary">
                            <i class="fas fa-arrow-left"></i> Annulla
                        </a>
                        <div>
                            <button type="button" class="btn btn-outline-primary me-2" id="preview-btn">
                                <i class="fas fa-eye"></i> Anteprima
                            </button>
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save"></i>
                                {% if view.object.pk %}Aggiorna{% else %}Salva{% endif %} Rappresentante
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </form>
    </div>
    
    <!-- Preview Modal -->
    <div class="modal fade" id="previewModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Anteprima Rappresentante</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="preview-content">
                    <!-- Content will be generated via JavaScript -->
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Chiudi</button>
                    <button type="button" class="btn btn-primary" onclick="document.getElementById('rappresentanteForm').submit();">
                        <i class="fas fa-save"></i> Conferma e Salva
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Real-time P.IVA validation
    const pivaField = document.getElementById('{{ form.partita_iva.id_for_label }}');
    const pivaValidation = document.getElementById('piva-validation');
    
    if (pivaField) {
        pivaField.addEventListener('blur', function() {
            const piva = this.value.trim();
            if (piva && piva.length === 11) {
                fetch('{% url "anagrafica:validate_partita_iva" %}?' + new URLSearchParams({
                    partita_iva: piva,
                    tipo: 'rappresentante',
                    exclude_id: '{{ view.object.pk|default:"" }}'
                }))
                .then(response => response.json())
                .then(data => {
                    pivaValidation.style.display = 'block';
                    pivaValidation.textContent = data.message;
                    pivaValidation.className = 'validation-message ' + (data.valid ? 'valid' : 'invalid');
                });
            } else {
                pivaValidation.style.display = 'none';
            }
        });
    }
    
    // Real-time CF validation
    const cfField = document.getElementById('{{ form.codice_fiscale.id_for_label }}');
    const cfValidation = document.getElementById('cf-validation');
    
    if (cfField) {
        cfField.addEventListener('blur', function() {
            const cf = this.value.trim().toUpperCase();
            this.value = cf; // Auto-uppercase
            if (cf && (cf.length === 11 || cf.length === 16)) {
                fetch('{% url "anagrafica:validate_codice_fiscale" %}?' + new URLSearchParams({
                    codice_fiscale: cf,
                    tipo: 'rappresentante',
                    exclude_id: '{{ view.object.pk|default:"" }}'
                }))
                .then(response => response.json())
                .then(data => {
                    cfValidation.style.display = 'block';
                    cfValidation.textContent = data.message;
                    cfValidation.className = 'validation-message ' + (data.valid ? 'valid' : 'invalid');
                });
            } else {
                cfValidation.style.display = 'none';
            }
        });
    }
    
    // Auto-uppercase provincia field
    const provinciaField = document.getElementById('{{ form.provincia.id_for_label }}');
    if (provinciaField) {
        provinciaField.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
        });
    }
    
    // Preview functionality
    document.getElementById('preview-btn').addEventListener('click', function() {
        const formData = new FormData(document.getElementById('rappresentanteForm'));
        const previewContent = document.getElementById('preview-content');
        
        let html = '<div class="preview-container">';
        html += '<h6 class="mb-3"><i class="fas fa-user-circle"></i> Informazioni Generali</h6>';
        html += '<p><strong>Nome:</strong> ' + (formData.get('nome') || 'Non specificato') + '</p>';
        html += '<p><strong>Ragione Sociale:</strong> ' + (formData.get('ragione_sociale') || 'Non specificato') + '</p>';
        html += '<p><strong>Indirizzo:</strong> ' + (formData.get('indirizzo') || 'Non specificato') + '</p>';
        html += '<p><strong>Città:</strong> ' + (formData.get('città') || 'Non specificato') + ' (' + (formData.get('provincia') || 'N/A') + ') ' + (formData.get('cap') || '') + '</p>';
        
        html += '<h6 class="mt-4 mb-3"><i class="fas fa-id-card"></i> Dati Fiscali</h6>';
        html += '<p><strong>Partita IVA:</strong> ' + (formData.get('partita_iva') || 'Non specificato') + '</p>';
        html += '<p><strong>Codice Fiscale:</strong> ' + (formData.get('codice_fiscale') || 'Non specificato') + '</p>';
        
        html += '<h6 class="mt-4 mb-3"><i class="fas fa-handshake"></i> Dati Commerciali</h6>';
        html += '<p><strong>Email:</strong> ' + (formData.get('email') || 'Non specificato') + '</p>';
        html += '<p><strong>Telefono:</strong> ' + (formData.get('telefono') || 'Non specificato') + '</p>';
        html += '<p><strong>Zona:</strong> ' + (formData.get('zona') || 'Non specificato') + '</p>';
        html += '<p><strong>Provvigioni:</strong> ' + (formData.get('percentuale_sulle_vendite') || '0') + '%</p>';
        html += '<p><strong>Stato:</strong> ' + (formData.get('attivo') ? 'Attivo' : 'Non attivo') + '</p>';
        html += '</div>';
        
        previewContent.innerHTML = html;
        new bootstrap.Modal(document.getElementById('previewModal')).show();
    });
});
</script>
{% endblock %}
```


### elenco.html

```html
{% extends 'base.html' %}
{% load static %}

{% block title %}Elenco Rappresentanti{% endblock %}

{% block extra_css %}
<style>
    .table-responsive {
        border-radius: 0.5rem;
        overflow: hidden;
    }
    .status-badge {
        font-size: 0.8rem;
    }
    .search-box {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .action-buttons .btn {
        margin-right: 0.2rem;
        margin-bottom: 0.5rem;
    }
</style>
{% endblock %}

{% block content %}
<div class="container-fluid">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h1 class="h3 mb-0 text-gray-800">Elenco Rappresentanti</h1>
            <p class="text-muted">Gestione rappresentanti commerciali</p>
        </div>
        <div class="btn-group" role="group">
            <a href="{% url 'anagrafica:nuovo_rappresentante' %}" class="btn btn-primary">
                <i class="fas fa-plus"></i> Nuovo Rappresentante
            </a>
            <button type="button" class="btn btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown">
                <i class="fas fa-cog"></i> Azioni
            </button>
            <ul class="dropdown-menu">
                <li><a class="dropdown-item" href="{% url 'anagrafica:export_anagrafica' %}?tipo=rappresentanti">
                    <i class="fas fa-download"></i> Esporta CSV
                </a></li>
                <li><a class="dropdown-item" href="{% url 'anagrafica:rappresentanti_pdf' %}">
                    <i class="fas fa-file-pdf"></i> Report PDF
                </a></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item" href="#" onclick="refreshStats()">
                    <i class="fas fa-sync"></i> Aggiorna Statistiche
                </a></li>
            </ul>
        </div>
    </div>

    <!-- Search/Filter Section -->
    <div class="search-box shadow-sm">
        <form method="get" class="row g-3">
            <div class="col-md-4">
                <label for="search" class="form-label">Cerca</label>
                <input type="text" class="form-control" id="search" name="search" 
                       value="{{ request.GET.search }}" placeholder="Nome, email, telefono...">
            </div>
            <div class="col-md-3">
                <label for="zona" class="form-label">Zona</label>
                <select class="form-select" id="zona" name="zona">
                    <option value="">Tutte le zone</option>
                    {% for zona in zone_list %}
                    <option value="{{ zona }}" {% if request.GET.zona == zona %}selected{% endif %}>
                        {{ zona }}
                    </option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-3">
                <label for="attivo" class="form-label">Stato</label>
                <select class="form-select" id="attivo" name="attivo">
                    <option value="True" {% if request.GET.attivo != 'False' %}selected{% endif %}>Attivi</option>
                    <option value="False" {% if request.GET.attivo == 'False' %}selected{% endif %}>Non attivi</option>
                </select>
            </div>
            <div class="col-md-2 d-flex align-items-end">
                <button type="submit" class="btn btn-primary w-100">
                    <i class="fas fa-search"></i> Cerca
                </button>
            </div>
        </form>
    </div>

    <!-- Statistics -->
    <div class="row mb-3">
        <div class="col-md-6">
            <div class="alert alert-info d-flex align-items-center" role="alert">
                <i class="fas fa-info-circle me-2"></i>
                <div>
                    Totale: <strong>{{ total_count }}</strong> rappresentanti
                    {% if request.GET.search or request.GET.zona %}
                    (filtrati)
                    {% endif %}
                </div>
            </div>
        </div>
        <div class="col-md-6 text-end">
            <div id="bulk-actions" class="d-none">
                <button class="btn btn-sm btn-warning" onclick="bulkActivate()">
                    <i class="fas fa-check"></i> Attiva Selezionati
                </button>
                <button class="btn btn-sm btn-secondary" onclick="bulkDeactivate()">
                    <i class="fas fa-times"></i> Disattiva Selezionati
                </button>
            </div>
        </div>
    </div>

    <!-- Table -->
    <div class="card shadow">
        <div class="card-body p-0">
            <div class="table-responsive">
                <table class="table table-hover mb-0">
                    <thead class="table-light">
                        <tr>
                            <th>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="selectAll">
                                </div>
                            </th>
                            <th>Nome</th>
                            <th>Ragione Sociale</th>
                            <th>Email</th>
                            <th>Telefono</th>
                            <th>Zona</th>
                            <th>Clienti</th>
                            <th>Provvigione</th>
                            <th>Stato</th>
                            <th>Azioni</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for rappresentante in rappresentanti %}
                        <tr>
                            <td>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" value="{{ rappresentante.id }}" 
                                           name="selected_items">
                                </div>
                            </td>
                            <td>
                                <div class="d-flex align-items-center">
                                    <div class="me-3">
                                        {% if rappresentante.user.foto_dipendente %}
                                        <img src="{{ rappresentante.user.foto_dipendente.url }}" 
                                             alt="{{ rappresentante.nome }}" 
                                             class="rounded-circle" width="40" height="40">
                                        {% else %}
                                        <div class="rounded-circle bg-primary d-flex align-items-center justify-content-center" 
                                             style="width: 40px; height: 40px;">
                                            <i class="fas fa-user text-white"></i>
                                        </div>
                                        {% endif %}
                                    </div>
                                    <div>
                                        <strong>{{ rappresentante.nome }}</strong>
                                        {% if rappresentante.user %}
                                        <br>
                                        <small class="text-muted">{{ rappresentante.user.username }}</small>
                                        {% endif %}
                                    </div>
                                </div>
                            </td>
                            <td>{{ rappresentante.ragione_sociale }}</td>
                            <td>
                                <a href="mailto:{{ rappresentante.email }}" class="text-decoration-none">
                                    {{ rappresentante.email }}
                                </a>
                            </td>
                            <td>
                                <a href="tel:{{ rappresentante.telefono }}" class="text-decoration-none">
                                    {{ rappresentante.telefono }}
                                </a>
                            </td>
                            <td>
                                {% if rappresentante.zona %}
                                <span class="badge bg-light text-dark">{{ rappresentante.zona }}</span>
                                {% else %}
                                <span class="text-muted">-</span>
                                {% endif %}
                            </td>
                            <td>
                                {% if rappresentante.clienti_count > 0 %}
                                <a href="{% url 'anagrafica:elenco_clienti' %}?rappresentante={{ rappresentante.id }}" 
                                   class="badge bg-success text-white">
                                    {{ rappresentante.clienti_count }} client{{ rappresentante.clienti_count|pluralize:'e,i' }}
                                </a>
                                {% else %}
                                <span class="badge bg-light text-muted">0 clienti</span>
                                {% endif %}
                            </td>
                            <td>{{ rappresentante.percentuale_sulle_vendite }}%</td>
                            <td>
                                {% if rappresentante.attivo %}
                                <span class="badge bg-success status-badge">
                                    <i class="fas fa-check"></i> Attivo
                                </span>
                                {% else %}
                                <span class="badge bg-danger status-badge">
                                    <i class="fas fa-times"></i> Non attivo
                                </span>
                                {% endif %}
                            </td>
                            <td>
                                <div class="action-buttons">
                                    <a href="{% url 'anagrafica:dettaglio_rappresentante' rappresentante.pk %}" 
                                       class="btn btn-sm btn-outline-primary" title="Visualizza">
                                        <i class="fas fa-eye"></i>
                                    </a>
                                    <a href="{% url 'anagrafica:modifica_rappresentante' rappresentante.pk %}" 
                                       class="btn btn-sm btn-outline-secondary" title="Modifica">
                                        <i class="fas fa-edit"></i>
                                    </a>
                                    <button type="button" class="btn btn-sm btn-outline-warning" 
                                            onclick="toggleActive({{ rappresentante.pk }}, {{ rappresentante.attivo|yesno:'false,true' }})"
                                            title="{% if rappresentante.attivo %}Disattiva{% else %}Attiva{% endif %}">
                                        <i class="fas fa-toggle-{% if rappresentante.attivo %}on{% else %}off{% endif %}"></i>
                                    </button>
                                    {% if not rappresentante.clienti_count %}
                                    <a href="{% url 'anagrafica:elimina_rappresentante' rappresentante.pk %}" 
                                       class="btn btn-sm btn-outline-danger" title="Elimina">
                                        <i class="fas fa-trash"></i>
                                    </a>
                                    {% endif %}
                                </div>
                            </td>
                        </tr>
                        {% empty %}
                        <tr>
                            <td colspan="10" class="text-center py-5 text-muted">
                                <i class="fas fa-inbox fa-2x mb-3"></i>
                                <br>
                                {% if request.GET.search %}
                                Nessun rappresentante trovato con i criteri specificati.
                                {% else %}
                                Nessun rappresentante presente. <a href="{% url 'anagrafica:nuovo_rappresentante' %}">Creane uno nuovo</a>.
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Pagination -->
    {% if is_paginated %}
    <nav aria-label="Page navigation" class="mt-4">
        <ul class="pagination justify-content-center">
            {% if page_obj.has_previous %}
            <li class="page-item">
                <a class="page-link" href="?{% if request.GET.search %}search={{ request.GET.search }}&{% endif %}{% if request.GET.zona %}zona={{ request.GET.zona }}&{% endif %}{% if request.GET.attivo %}attivo={{ request.GET.attivo }}&{% endif %}page=1">
                    <i class="fas fa-angle-double-left"></i>
                </a>
            </li>
            <li class="page-item">
                <a class="page-link" href="?{% if request.GET.search %}search={{ request.GET.search }}&{% endif %}{% if request.GET.zona %}zona={{ request.GET.zona }}&{% endif %}{% if request.GET.attivo %}attivo={{ request.GET.attivo }}&{% endif %}page={{ page_obj.previous_page_number }}">
                    <i class="fas fa-angle-left"></i>
                </a>
            </li>
            {% endif %}
            
            <li class="page-item active">
                <span class="page-link">
                    Pagina {{ page_obj.number }} di {{ page_obj.paginator.num_pages }}
                </span>
            </li>
            
            {% if page_obj.has_next %}
            <li class="page-item">
                <a class="page-link" href="?{% if request.GET.search %}search={{ request.GET.search }}&{% endif %}{% if request.GET.zona %}zona={{ request.GET.zona }}&{% endif %}{% if request.GET.attivo %}attivo={{ request.GET.attivo }}&{% endif %}page={{ page_obj.next_page_number }}">
                    <i class="fas fa-angle-right"></i>
                </a>
            </li>
            <li class="page-item">
                <a class="page-link" href="?{% if request.GET.search %}search={{ request.GET.search }}&{% endif %}{% if request.GET.zona %}zona={{ request.GET.zona }}&{% endif %}{% if request.GET.attivo %}attivo={{ request.GET.attivo }}&{% endif %}page={{ page_obj.paginator.num_pages }}">
                    <i class="fas fa-angle-double-right"></i>
                </a>
            </li>
            {% endif %}
        </ul>
    </nav>
    {% endif %}
</div>
{% endblock %}

{% block extra_js %}
<script>
// Select all functionality
document.getElementById('selectAll').addEventListener('change', function() {
    const checkboxes = document.querySelectorAll('input[name="selected_items"]');
    const bulkActions = document.getElementById('bulk-actions');
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = this.checked;
    });
    
    if (this.checked) {
        bulkActions.classList.remove('d-none');
    } else {
        bulkActions.classList.add('d-none');
    }
});

// Show bulk actions when any checkbox is selected
document.querySelectorAll('input[name="selected_items"]').forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        const selected = document.querySelectorAll('input[name="selected_items"]:checked');
        const bulkActions = document.getElementById('bulk-actions');
        
        if (selected.length > 0) {
            bulkActions.classList.remove('d-none');
        } else {
            bulkActions.classList.add('d-none');
        }
    });
});

// Toggle active/inactive status
function toggleActive(id, newStatus) {
    if (confirm('Sei sicuro di voler ' + (newStatus ? 'attivare' : 'disattivare') + ' questo rappresentante?')) {
        // AJAX call to toggle status
        fetch(`{% url 'anagrafica:toggle_attivo' 'rappresentante' 0 %}`.replace('0', id), {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json',
            },
        }).then(response => {
            if (response.ok) {
                location.reload();
            } else {
                alert('Errore durante l\'operazione');
            }
        });
    }
}

// Bulk activate
function bulkActivate() {
    const selected = document.querySelectorAll('input[name="selected_items"]:checked');
    const ids = Array.from(selected).map(checkbox => checkbox.value);
    
    if (ids.length === 0) {
        alert('Seleziona almeno un rappresentante');
        return;
    }
    
    if (confirm(`Attivare ${ids.length} rappresentanti selezionati?`)) {
        // AJAX call for bulk activation
        fetch('{% url "anagrafica:attiva_multipli" %}', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                'tipo': 'rappresentante',
                'ids': ids
            })
        }).then(response => {
            if (response.ok) {
                location.reload();
            }
        });
    }
}

// Bulk deactivate
function bulkDeactivate() {
    const selected = document.querySelectorAll('input[name="selected_items"]:checked');
    const ids = Array.from(selected).map(checkbox => checkbox.value);
    
    if (ids.length === 0) {
        alert('Seleziona almeno un rappresentante');
        return;
    }
    
    if (confirm(`Disattivare ${ids.length} rappresentanti selezionati?`)) {
        fetch('{% url "anagrafica:disattiva_multipli" %}', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                'tipo': 'rappresentante',
                'ids': ids
            })
        }).then(response => {
            if (response.ok) {
                location.reload();
            }
        });
    }
}

// Refresh stats
function refreshStats() {
    fetch('{% url "anagrafica:dashboard_stats_api" %}')
        .then(response => response.json())
        .then(data => {
            // Update any stats display if needed
            alert('Statistiche aggiornate!');
        });
}
</script>
{% endblock %}
```


### dettaglio.html

```html
{% extends 'base.html' %}
{% load static %}

{% block title %}{{ rappresentante.nome }} - Dettagli{% endblock %}

{% block extra_css %}
<style>
    .profile-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 2rem;
        margin-bottom: 2rem;
    }
    .info-card {
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    .info-label {
        font-weight: 600;
        color: #6c757d;
        font-size: 0.9rem;
    }
    .info-value {
        font-size: 1.1rem;
        color: #495057;
    }
    .status-badge {
        font-size: 1rem;
        padding: 0.5rem 1rem;
    }
    .activity-item {
        border-left: 3px solid #007bff;
        padding-left: 1rem;
        margin-bottom: 1rem;
    }
    .stats-card {
        text-align: center;
        padding: 1.5rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    .stats-number {
        font-size: 2.5rem;
        font-weight: bold;
    }
    .quick-actions .btn {
        margin: 0.25rem;
    }
</style>
{% endblock %}

{% block content %}
<div class="container-fluid">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="{% url 'anagrafica:dashboard' %}">Anagrafica</a></li>
                    <li class="breadcrumb-item"><a href="{% url 'anagrafica:elenco_rappresentanti' %}">Rappresentanti</a></li>
                    <li class="breadcrumb-item active">{{ rappresentante.nome }}</li>
                </ol>
            </nav>
            <h1 class="h3 mb-0">Dettagli Rappresentante</h1>
        </div>
        <div class="quick-actions">
            <a href="{% url 'anagrafica:modifica_rappresentante' rappresentante.pk %}" class="btn btn-primary">
                <i class="fas fa-edit"></i> Modifica
            </a>
            <button class="btn btn-warning" onclick="toggleStatus('{{ rappresentante.pk }}', '{{ rappresentante.attivo|yesno:'false,true' }}')">
                <i class="fas fa-toggle-{% if rappresentante.attivo %}on{% else %}off{% endif %}"></i>
                {% if rappresentante.attivo %}Disattiva{% else %}Attiva{% endif %}
            </button>
            {% if not rappresentante.clienti.count %}
            <a href="{% url 'anagrafica:elimina_rappresentante' rappresentante.pk %}" 
               class="btn btn-danger" onclick="return confirm('Sei sicuro di voler eliminare questo rappresentante?')">
                <i class="fas fa-trash"></i> Elimina
            </a>
            {% endif %}
            <div class="btn-group" role="group">
                <button class="btn btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                    <i class="fas fa-cog"></i> Azioni
                </button>
                <ul class="dropdown-menu">
                    <li><a class="dropdown-item" href="mailto:{{ rappresentante.email }}">
                        <i class="fas fa-envelope"></i> Invia Email
                    </a></li>
                    <li><a class="dropdown-item" href="tel:{{ rappresentante.telefono }}">
                        <i class="fas fa-phone"></i> Chiama
                    </a></li>
                    <li><hr class="dropdown-divider"></li>
                    <li><a class="dropdown-item" href="#" onclick="exportData()">
                        <i class="fas fa-download"></i> Esporta Dati
                    </a></li>
                </ul>
            </div>
        </div>
    </div>

    <!-- Profile Card -->
    <div class="profile-card">
        <div class="row align-items-center">
            <div class="col-md-3 text-center">
                {% if rappresentante.user and rappresentante.user.foto_dipendente %}
                    <img src="{{ rappresentante.user.foto_dipendente.url }}" alt="{{ rappresentante.nome }}" 
                         class="rounded-circle img-thumbnail bg-white p-1" style="width: 120px; height: 120px;">
                {% else %}
                    <div class="rounded-circle bg-white d-flex align-items-center justify-content-center mx-auto" 
                         style="width: 120px; height: 120px;">
                        <i class="fas fa-user fa-4x text-primary"></i>
                    </div>
                {% endif %}
            </div>
            <div class="col-md-9">
                <h2 class="mb-3">{{ rappresentante.nome }}</h2>
                <div class="row">
                    <div class="col-md-6">
                        <p class="mb-2"><i class="fas fa-building me-2"></i> {{ rappresentante.ragione_sociale }}</p>
                        <p class="mb-2"><i class="fas fa-envelope me-2"></i> {{ rappresentante.email }}</p>
                        <p class="mb-2"><i class="fas fa-phone me-2"></i> {{ rappresentante.telefono }}</p>
                    </div>
                    <div class="col-md-6">
                        <p class="mb-2"><i class="fas fa-map-marker-alt me-2"></i> {{ rappresentante.zona|default:"Nessuna zona" }}</p>
                        <p class="mb-2"><i class="fas fa-percentage me-2"></i> {{ rappresentante.percentuale_sulle_vendite }}% provvigioni</p>
                        <p class="mb-0">
                            <i class="fas fa-circle me-2"></i>
                            <span class="badge status-badge {% if rappresentante.attivo %}bg-success{% else %}bg-danger{% endif %}">
                                {% if rappresentante.attivo %}Attivo{% else %}Non Attivo{% endif %}
                            </span>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Statistics Cards -->
    <div class="row mb-4">
        <div class="col-md-3">
            <div class="stats-card">
                <div class="stats-number">{{ clienti_count }}</div>
                <div class="stats-label">Clienti Attivi</div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="stats-card" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);">
                <div class="stats-number">€ 0</div>
                <div class="stats-label">Vendite Totali</div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="stats-card" style="background: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%);">
                <div class="stats-number">€ 0</div>
                <div class="stats-label">Provvigioni</div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="stats-card" style="background: linear-gradient(135deg, #a8e6cf 0%, #dcedc8 100%);">
                <div class="stats-number">{{ rappresentante.data_creazione|timesince }}</div>
                <div class="stats-label">fa</div>
            </div>
        </div>
    </div>

    <!-- Detailed Information -->
    <div class="row">
        <!-- Informazioni Anagrafiche -->
        <div class="col-md-6">
            <div class="card info-card">
                <div class="card-header bg-primary text-white">
                    <h5 class="card-title mb-0">
                        <i class="fas fa-id-card me-2"></i>
                        Informazioni Anagrafiche
                    </h5>
                </div>
                <div class="card-body">
                    <div class="row mb-3">
                        <div class="col-sm-4 info-label">Nome Completo:</div>
                        <div class="col-sm-8 info-value">{{ rappresentante.nome }}</div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-sm-4 info-label">Ragione Sociale:</div>
                        <div class="col-sm-8 info-value">{{ rappresentante.ragione_sociale }}</div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-sm-4 info-label">Indirizzo:</div>
                        <div class="col-sm-8 info-value">
                            {{ rappresentante.indirizzo }}<br>
                            {{ rappresentante.cap }} {{ rappresentante.città }} ({{ rappresentante.provincia }})
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-sm-4 info-label">Partita IVA:</div>
                        <div class="col-sm-8 info-value">{{ rappresentante.partita_iva }}</div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-sm-4 info-label">Codice Fiscale:</div>
                        <div class="col-sm-8 info-value">{{ rappresentante.codice_fiscale }}</div>
                    </div>
                    <div class="row mb-0">
                        <div class="col-sm-4 info-label">Codice Univoco:</div>
                        <div class="col-sm-8 info-value">{{ rappresentante.codice_univoco|default:"Non specificato" }}</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Informazioni Utente -->
        <div class="col-md-6">
            <div class="card info-card">
                <div class="card-header bg-success text-white">
                    <h5 class="card-title mb-0">
                        <i class="fas fa-user me-2"></i>
                        Informazioni Utente
                    </h5>
                </div>
                <div class="card-body">
                    {% if rappresentante.user %}
                    <div class="row mb-3">
                        <div class="col-sm-4 info-label">Username:</div>
                        <div class="col-sm-8 info-value">
                            <a href="{% url 'dipendenti:vedidipendente' rappresentante.user.pk %}" class="text-decoration-none">
                                {{ rappresentante.user.username }}
                            </a>
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-sm-4 info-label">Nome Completo:</div>
                        <div class="col-sm-8 info-value">{{ rappresentante.user.get_full_name|default:"Non specificato" }}</div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-sm-4 info-label">Livello:</div>
                        <div class="col-sm-8 info-value">
                            <span class="badge bg-info">{{ rappresentante.user.get_livello_display }}</span>
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-sm-4 info-label">Data Assunzione:</div>
                        <div class="col-sm-8 info-value">{{ rappresentante.user.data_assunzione|date:"d/m/Y"|default:"Non specificata" }}</div>
                    </div>
                    <div class="row mb-0">
                        <div class="col-sm-4 info-label">Stato Utente:</div>
                        <div class="col-sm-8 info-value">
                            <span class="badge {% if rappresentante.user.is_active %}bg-success{% else %}bg-danger{% endif %}">
                                {% if rappresentante.user.is_active %}Attivo{% else %}Disattivato{% endif %}
                            </span>
                        </div>
                    </div>
                    {% else %}
                    <div class="alert alert-warning" role="alert">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Nessun utente associato a questo rappresentante.
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>

    <!-- Clienti del Rappresentante -->
    <div class="row mt-4">
        <div class="col-12">
            <div class="card info-card">
                <div class="card-header bg-info text-white d-flex justify-content-between align-items-center">
                    <h5 class="card-title mb-0">
                        <i class="fas fa-users me-2"></i>
                        Clienti Associati ({{ clienti.count }})
                    </h5>
                    <a href="{% url 'anagrafica:nuovo_cliente' %}?rappresentante={{ rappresentante.pk }}" 
                       class="btn btn-light btn-sm">
                        <i class="fas fa-plus"></i> Aggiungi Cliente
                    </a>
                </div>
                <div class="card-body">
                    {% if clienti %}
                    <div class="table-responsive">
                        <table class="table table-striped table-hover">
                            <thead>
                                <tr>
                                    <th>Ragione Sociale</th>
                                    <th>Città</th>
                                    <th>Email</th>
                                    <th>Telefono</th>
                                    <th>Pagamento</th>
                                    <th>Stato</th>
                                    <th>Azioni</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for cliente in clienti %}
                                <tr>
                                    <td>
                                        <a href="{% url 'anagrafica:dettaglio_cliente' cliente.pk %}" class="text-decoration-none">
                                            {{ cliente.ragione_sociale }}
                                        </a>
                                    </td>
                                    <td>{{ cliente.città }}</td>
                                    <td>
                                        <a href="mailto:{{ cliente.email }}" class="text-decoration-none">
                                            {{ cliente.email }}
                                        </a>
                                    </td>
                                    <td>
                                        <a href="tel:{{ cliente.telefono }}" class="text-decoration-none">
                                            {{ cliente.telefono }}
                                        </a>
                                    </td>
                                    <td>
                                        <span class="badge bg-light text-dark">
                                            {{ cliente.get_pagamento_display }}
                                        </span>
                                    </td>
                                    <td>
                                        <span class="badge {% if cliente.attivo %}bg-success{% else %}bg-danger{% endif %}">
                                            {% if cliente.attivo %}Attivo{% else %}Non attivo{% endif %}
                                        </span>
                                    </td>
                                    <td>
                                        <div class="btn-group" role="group" aria-label="Azioni">
                                            <a href="{% url 'anagrafica:dettaglio_cliente' cliente.pk %}" 
                                               class="btn btn-sm btn-outline-primary" title="Visualizza">
                                                <i class="fas fa-eye"></i>
                                            </a>
                                            <a href="{% url 'anagrafica:modifica_cliente' cliente.pk %}" 
                                               class="btn btn-sm btn-outline-secondary" title="Modifica">
                                                <i class="fas fa-edit"></i>
                                            </a>
                                        </div>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% else %}
                    <div class="alert alert-light" role="alert">
                        <div class="text-center">
                            <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                            <h5 class="text-muted">Nessun cliente associato</h5>
                            <p class="text-muted">Questo rappresentante non ha ancora clienti associati.</p>
                            <a href="{% url 'anagrafica:nuovo_cliente' %}?rappresentante={{ rappresentante.pk }}" 
                               class="btn btn-primary">
                                <i class="fas fa-plus"></i> Aggiungi Primo Cliente
                            </a>
                        </div>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>

    <!-- Note -->
    {% if rappresentante.note %}
    <div class="row mt-4">
        <div class="col-12">
            <div class="card info-card">
                <div class="card-header bg-secondary text-white">
                    <h5 class="card-title mb-0">
                        <i class="fas fa-sticky-note me-2"></i>
                        Note
                    </h5>
                </div>
                <div class="card-body">
                    {{ rappresentante.note|linebreaks }}
                </div>
            </div>
        </div>
    </div>
    {% endif %}
</div>
{% endblock %}

{% block extra_js %}
<script>
function toggleStatus(id, newStatus) {
    if (confirm('Sei sicuro di voler ' + (newStatus === 'true' ? 'attivare' : 'disattivare') + ' questo rappresentante?')) {
        fetch(`{% url 'anagrafica:toggle_attivo' 'rappresentante' 0 %}`.replace('0', id), {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json',
            },
        }).then(response => {
            if (response.ok) {
                location.reload();
            } else {
                alert('Errore durante l\'operazione');
            }
        });
    }
}

function exportData() {
    // Crea un URL per export dati del rappresentante
    const exportUrl = `{% url 'anagrafica:export_anagrafica' %}?tipo=rappresentante&id={{ rappresentante.pk }}`;
    window.open(exportUrl, '_blank');
}

// Tooltip initialization
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
</script>
{% endblock %}
```


### modifica.html

```html
{% extends 'base.html' %}
{% load static %}
{% load crispy_forms_tags %}

{% block title %}
{% if view.object.pk %}Modifica Rappresentante{% else %}Nuovo Rappresentante{% endif %}
{% endblock %}

{% block extra_css %}
<style>
    .form-container {
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        padding: 2rem;
        margin-top: 1rem;
    }
    
    .step-indicator {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .navbar {
        margin-bottom: 0;
    }
    
    .tab-content {
        padding: 1.5rem 0;
        border-top: 2px solid #e9ecef;
    }
    
    .nav-tabs {
        background-color: #f8f9fa;
        border-radius: 8px 8px 0 0;
        padding: 0.5rem;
    }
    
    .nav-tabs .nav-link {
        border: none;
        border-radius: 25px;
        margin-right: 0.5rem;
        padding: 0.75rem 1.5rem;
        color: #667eea;
        font-weight: 500;
        transition: all 0.3s ease;
        background-color: transparent;
    }
    
    .nav-tabs .nav-link:hover {
        background-color: rgba(102, 126, 234, 0.1);
        color: #5a6ab8;
    }
    
    .nav-tabs .nav-link.active {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: transparent;
    }
    
    .form-label {
        color: #495057;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .form-control, .form-select {
        border: 2px solid #e9ecef;
        border-radius: 8px;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .form-control:focus, .form-select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
    }
    
    .btn-primary {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    .btn-secondary {
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
    }
    
    .required-field::after {
        content: ' *';
        color: #dc3545;
    }
    
    .field-help {
        font-size: 0.875rem;
        color: #6c757d;
        margin-top: 0.25rem;
    }
    
    .validation-message {
        background-color: #f8f9fa;
        border: 1px solid #e2e2e8;
        border-radius: 8px;
        padding: 0.75rem;
        margin-top: 0.5rem;
        font-size: 0.875rem;
    }
    
    .validation-message.valid {
        border-color: #28a745;
        color: #155724;
        background-color: #d4edda;
    }
    
    .validation-message.invalid {
        border-color: #dc3545;
        color: #721c24;
        background-color: #f8d7da;
    }
    
    .tab-pane {
        background-color: white;
        border-radius: 0 0 8px 8px;
        border: 1px solid #e9ecef;
        border-top: none;
        padding: 1.5rem;
    }
</style>
{% endblock %}

{% block content %}
<div class="container-fluid">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="{% url 'anagrafica:dashboard' %}">Anagrafica</a></li>
                    <li class="breadcrumb-item"><a href="{% url 'anagrafica:elenco_rappresentanti' %}">Rappresentanti</a></li>
                    <li class="breadcrumb-item active">
                        {% if view.object.pk %}Modifica{% else %}Nuovo{% endif %}
                    </li>
                </ol>
            </nav>
            <h1 class="h3 mb-0">
                {% if view.object.pk %}
                    <i class="fas fa-edit"></i> Modifica Rappresentante
                {% else %}
                    <i class="fas fa-plus"></i> Nuovo Rappresentante
                {% endif %}
            </h1>
        </div>
    </div>

    <!-- Step Indicator -->
    <div class="step-indicator">
        <h4 class="mb-0">
            {% if view.object.pk %}
                Modifica i dati del rappresentante {{ view.object.nome }}
            {% else %}
                Inserimento nuovo rappresentante
            {% endif %}
        </h4>
        <p class="mb-0 mt-2 opacity-75">
            Completa tutti i campi obbligatori per salvare il rappresentante
        </p>
    </div>

    <!-- Form Container -->
    <div class="form-container">
        <form method="post" id="rappresentanteForm">
            {% csrf_token %}
            
            <!-- Form Errors (if any) -->
            {% if form.non_field_errors %}
            <div class="alert alert-danger" role="alert">
                <h5 class="alert-heading"><i class="fas fa-exclamation-triangle"></i> Errori di validazione</h5>
                {% for error in form.non_field_errors %}
                    <p class="mb-0">{{ error }}</p>
                {% endfor %}
            </div>
            {% endif %}
            
            <!-- Tabs Navigation -->
            <ul class="nav nav-tabs" id="formTabs" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="general-tab" data-bs-toggle="tab" 
                            data-bs-target="#general" type="button" role="tab">
                        <i class="fas fa-user-circle"></i> Informazioni Generali
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="fiscal-tab" data-bs-toggle="tab" 
                            data-bs-target="#fiscal" type="button" role="tab">
                        <i class="fas fa-id-card"></i> Dati Fiscali
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="commercial-tab" data-bs-toggle="tab" 
                            data-bs-target="#commercial" type="button" role="tab">
                        <i class="fas fa-handshake"></i> Dati Commerciali
                    </button>
                </li>
            </ul>
            
            <!-- Tab Content -->
            <div class="tab-content" id="formTabContent">
                <!-- Tab 1: Informazioni Generali -->
                <div class="tab-pane fade show active" id="general" role="tabpanel">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.user.id_for_label }}" class="form-label">
                                    <i class="fas fa-user me-2"></i>Utente Associato
                                </label>
                                {{ form.user|add_class:"form-select" }}
                                {% if form.user.errors %}
                                    <div class="invalid-feedback d-block">{{ form.user.errors|join:', ' }}</div>
                                {% endif %}
                                <div class="field-help">Seleziona l'utente dipendente da associare al rappresentante</div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.nome.id_for_label }}" class="form-label required-field">
                                    <i class="fas fa-signature me-2"></i>Nome Completo
                                </label>
                                {{ form.nome|add_class:"form-control" }}
                                {% if form.nome.errors %}
                                    <div class="invalid-feedback d-block">{{ form.nome.errors|join:', ' }}</div>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-12">
                            <div class="mb-3">
                                <label for="{{ form.ragione_sociale.id_for_label }}" class="form-label required-field">
                                    <i class="fas fa-building me-2"></i>Ragione Sociale
                                </label>
                                {{ form.ragione_sociale|add_class:"form-control" }}
                                {% if form.ragione_sociale.errors %}
                                    <div class="invalid-feedback d-block">{{ form.ragione_sociale.errors|join:', ' }}</div>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-8">
                            <div class="mb-3">
                                <label for="{{ form.indirizzo.id_for_label }}" class="form-label">
                                    <i class="fas fa-map-marker-alt me-2"></i>Indirizzo
                                </label>
                                {{ form.indirizzo|add_class:"form-control" }}
                                {% if form.indirizzo.errors %}
                                    <div class="invalid-feedback d-block">{{ form.indirizzo.errors|join:', ' }}</div>
                                {% endif %}
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="mb-3">
                                <label for="{{ form.cap.id_for_label }}" class="form-label">
                                    CAP
                                </label>
                                {{ form.cap|add_class:"form-control" }}
                                {% if form.cap.errors %}
                                    <div class="invalid-feedback d-block">{{ form.cap.errors|join:', ' }}</div>
                                {% endif %}
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="mb-3">
                                <label for="{{ form.provincia.id_for_label }}" class="form-label">
                                    Provincia
                                </label>
                                {{ form.provincia|add_class:"form-control" }}
                                {% if form.provincia.errors %}
                                    <div class="invalid-feedback d-block">{{ form.provincia.errors|join:', ' }}</div>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-8">
                            <div class="mb-3">
                                <label for="{{ form.città.id_for_label }}" class="form-label">
                                    <i class="fas fa-city me-2"></i>Città
                                </label>
                                {{ form.città|add_class:"form-control" }}
                                {% if form.città.errors %}
                                    <div class="invalid-feedback d-block">{{ form.città.errors|join:', ' }}</div>
                                {% endif %}
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="mb-3">
                                <label for="{{ form.zona.id_for_label }}" class="form-label">
                                    <i class="fas fa-globe-europe me-2"></i>Zona di Competenza
                                </label>
                                {{ form.zona|add_class:"form-control" }}
                                {% if form.zona.errors %}
                                    <div class="invalid-feedback d-block">{{ form.zona.errors|join:', ' }}</div>
                                {% endif %}
                                <div class="field-help">Es: Nord Italia, Lombardia, ecc.</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Tab 2: Dati Fiscali -->
                <div class="tab-pane fade" id="fiscal" role="tabpanel">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.partita_iva.id_for_label }}" class="form-label required-field">
                                    <i class="fas fa-file-invoice me-2"></i>Partita IVA
                                </label>
                                {{ form.partita_iva|add_class:"form-control" }}
                                {% if form.partita_iva.errors %}
                                    <div class="invalid-feedback d-block">{{ form.partita_iva.errors|join:', ' }}</div>
                                {% endif %}
                                <div class="validation-message" id="piva-validation" style="display: none;"></div>
                                <div class="field-help">11 cifre numeriche</div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.codice_fiscale.id_for_label }}" class="form-label required-field">
                                    <i class="fas fa-id-badge me-2"></i>Codice Fiscale
                                </label>
                                {{ form.codice_fiscale|add_class:"form-control" }}
                                {% if form.codice_fiscale.errors %}
                                    <div class="invalid-feedback d-block">{{ form.codice_fiscale.errors|join:', ' }}</div>
                                {% endif %}
                                <div class="validation-message" id="cf-validation" style="display: none;"></div>
                                <div class="field-help">16 caratteri per persona fisica o 11 cifre per azienda</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.codice_univoco.id_for_label }}" class="form-label">
                                    <i class="fas fa-qrcode me-2"></i>Codice Univoco
                                </label>
                                {{ form.codice_univoco|add_class:"form-control" }}
                                {% if form.codice_univoco.errors %}
                                    <div class="invalid-feedback d-block">{{ form.codice_univoco.errors|join:', ' }}</div>
                                {% endif %}
                                <div class="field-help">Codice destinatario per fatturazione elettronica</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Tab 3: Dati Commerciali -->
                <div class="tab-pane fade" id="commercial" role="tabpanel">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.telefono.id_for_label }}" class="form-label required-field">
                                    <i class="fas fa-phone me-2"></i>Telefono
                                </label>
                                {{ form.telefono|add_class:"form-control" }}
                                {% if form.telefono.errors %}
                                    <div class="invalid-feedback d-block">{{ form.telefono.errors|join:', ' }}</div>
                                {% endif %}
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.email.id_for_label }}" class="form-label required-field">
                                    <i class="fas fa-envelope me-2"></i>Email
                                </label>
                                {{ form.email|add_class:"form-control" }}
                                {% if form.email.errors %}
                                    <div class="invalid-feedback d-block">{{ form.email.errors|join:', ' }}</div>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="{{ form.percentuale_sulle_vendite.id_for_label }}" class="form-label required-field">
                                    <i class="fas fa-percentage me-2"></i>Percentuale Provvigioni (%)
                                </label>
                                {{ form.percentuale_sulle_vendite|add_class:"form-control" }}
                                {% if form.percentuale_sulle_vendite.errors %}
                                    <div class="invalid-feedback d-block">{{ form.percentuale_sulle_vendite.errors|join:', ' }}</div>
                                {% endif %}
                                <div class="field-help">Inserire un valore tra 0 e 100</div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3 d-flex align-items-center">
                                <div class="form-check">
                                    {{ form.attivo }}
                                    <label class="form-check-label" for="{{ form.attivo.id_for_label }}">
                                        <i class="fas fa-check-circle me-2"></i>Rappresentante Attivo
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-12">
                            <div class="mb-3">
                                <label for="{{ form.note.id_for_label }}" class="form-label">
                                    <i class="fas fa-sticky-note me-2"></i>Note Aggiuntive
                                </label>
                                {{ form.note|add_class:"form-control" }}
                                {% if form.note.errors %}
                                    <div class="invalid-feedback d-block">{{ form.note.errors|join:', ' }}</div>
                                {% endif %}
                                <div class="field-help">Note interne, non visibili al rappresentante</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Footer Buttons -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="d-flex justify-content-between">
                        <a href="{% url 'anagrafica:elenco_rappresentanti' %}" class="btn btn-secondary">
                            <i class="fas fa-arrow-left"></i> Annulla
                        </a>
                        <div>
                            <button type="button" class="btn btn-outline-primary me-2" id="preview-btn">
                                <i class="fas fa-eye"></i> Anteprima
                            </button>
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save"></i>
                                {% if view.object.pk %}Aggiorna{% else %}Salva{% endif %} Rappresentante
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </form>
    </div>
    
    <!-- Preview Modal -->
    <div class="modal fade" id="previewModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Anteprima Rappresentante</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="preview-content">
                    <!-- Content will be generated via JavaScript -->
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Chiudi</button>
                    <button type="button" class="btn btn-primary" onclick="document.getElementById('rappresentanteForm').submit();">
                        <i class="fas fa-save"></i> Conferma e Salva
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Real-time P.IVA validation
    const pivaField = document.getElementById('{{ form.partita_iva.id_for_label }}');
    const pivaValidation = document.getElementById('piva-validation');
    
    if (pivaField) {
        pivaField.addEventListener('blur', function() {
            const piva = this.value.trim();
            if (piva && piva.length === 11) {
                fetch('{% url "anagrafica:validate_partita_iva" %}?' + new URLSearchParams({
                    partita_iva: piva,
                    tipo: 'rappresentante',
                    exclude_id: '{{ view.object.pk|default:"" }}'
                }))
                .then(response => response.json())
                .then(data => {
                    pivaValidation.style.display = 'block';
                    pivaValidation.textContent = data.message;
                    pivaValidation.className = 'validation-message ' + (data.valid ? 'valid' : 'invalid');
                });
            } else {
                pivaValidation.style.display = 'none';
            }
        });
    }
    
    // Real-time CF validation
    const cfField = document.getElementById('{{ form.codice_fiscale.id_for_label }}');
    const cfValidation = document.getElementById('cf-validation');
    
    if (cfField) {
        cfField.addEventListener('blur', function() {
            const cf = this.value.trim().toUpperCase();
            this.value = cf; // Auto-uppercase
            if (cf && (cf.length === 11 || cf.length === 16)) {
                fetch('{% url "anagrafica:validate_codice_fiscale" %}?' + new URLSearchParams({
                    codice_fiscale: cf,
                    tipo: 'rappresentante',
                    exclude_id: '{{ view.object.pk|default:"" }}'
                }))
                .then(response => response.json())
                .then(data => {
                    cfValidation.style.display = 'block';
                    cfValidation.textContent = data.message;
                    cfValidation.className = 'validation-message ' + (data.valid ? 'valid' : 'invalid');
                });
            } else {
                cfValidation.style.display = 'none';
            }
        });
    }
    
    // Auto-uppercase provincia field
    const provinciaField = document.getElementById('{{ form.provincia.id_for_label }}');
    if (provinciaField) {
        provinciaField.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
        });
    }
    
    // Preview functionality
    document.getElementById('preview-btn').addEventListener('click', function() {
        const formData = new FormData(document.getElementById('rappresentanteForm'));
        const previewContent = document.getElementById('preview-content');
        
        let html = '<div class="preview-container">';
        html += '<h6 class="mb-3"><i class="fas fa-user-circle"></i> Informazioni Generali</h6>';
        html += '<p><strong>Nome:</strong> ' + (formData.get('nome') || 'Non specificato') + '</p>';
        html += '<p><strong>Ragione Sociale:</strong> ' + (formData.get('ragione_sociale') || 'Non specificato') + '</p>';
        html += '<p><strong>Indirizzo:</strong> ' + (formData.get('indirizzo') || 'Non specificato') + '</p>';
        html += '<p><strong>Città:</strong> ' + (formData.get('città') || 'Non specificato') + ' (' + (formData.get('provincia') || 'N/A') + ') ' + (formData.get('cap') || '') + '</p>';
        
        html += '<h6 class="mt-4 mb-3"><i class="fas fa-id-card"></i> Dati Fiscali</h6>';
        html += '<p><strong>Partita IVA:</strong> ' + (formData.get('partita_iva') || 'Non specificato') + '</p>';
        html += '<p><strong>Codice Fiscale:</strong> ' + (formData.get('codice_fiscale') || 'Non specificato') + '</p>';
        
        html += '<h6 class="mt-4 mb-3"><i class="fas fa-handshake"></i> Dati Commerciali</h6>';
        html += '<p><strong>Email:</strong> ' + (formData.get('email') || 'Non specificato') + '</p>';
        html += '<p><strong>Telefono:</strong> ' + (formData.get('telefono') || 'Non specificato') + '</p>';
        html += '<p><strong>Zona:</strong> ' + (formData.get('zona') || 'Non specificato') + '</p>';
        html += '<p><strong>Provvigioni:</strong> ' + (formData.get('percentuale_sulle_vendite') || '0') + '%</p>';
        html += '<p><strong>Stato:</strong> ' + (formData.get('attivo') ? 'Attivo' : 'Non attivo') + '</p>';
        html += '</div>';
        
        previewContent.innerHTML = html;
        new bootstrap.Modal(document.getElementById('previewModal')).show();
    });
});
</script>
{% endblock %}
```

