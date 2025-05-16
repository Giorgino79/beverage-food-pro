# automezzi/forms.py

from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, HTML, Div
from crispy_forms.bootstrap import FormActions
from .models import (
    TipoCarburante, Automezzo, DocumentoAutomezzo, 
    Manutenzione, RifornimentoCarburante, EventoAutomezzo
)


class DateInput(forms.DateInput):
    """Widget personalizzato per date"""
    input_type = 'date'


class TipoCarburanteForm(forms.ModelForm):
    """Form per la gestione dei tipi di carburante"""
    
    class Meta:
        model = TipoCarburante
        fields = ['nome', 'costo_per_litro']
        widgets = {
            'costo_per_litro': forms.NumberInput(attrs={'step': '0.001', 'min': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Dati Carburante',
                Row(
                    Column('nome', css_class='form-group col-md-8'),
                    Column('costo_per_litro', css_class='form-group col-md-4'),
                ),
            ),
            FormActions(
                Submit('submit', 'Salva', css_class='btn btn-primary'),
            )
        )


class AutomezzoForm(forms.ModelForm):
    """Form per la gestione degli automezzi"""
    
    class Meta:
        model = Automezzo
        fields = [
            'targa', 'marca', 'modello', 'anno_immatricolazione',
            'numero_telaio', 'tipo_carburante', 'cilindrata', 'potenza',
            'chilometri_iniziali', 'chilometri_attuali',
            'data_acquisto', 'costo_acquisto', 'assegnato_a',
            'attivo', 'disponibile', 'note'
        ]
        widgets = {
            'targa': forms.TextInput(attrs={'style': 'text-transform: uppercase;'}),
            'data_acquisto': DateInput(),
            'costo_acquisto': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'chilometri_iniziali': forms.NumberInput(attrs={'min': '0'}),
            'chilometri_attuali': forms.NumberInput(attrs={'min': '0'}),
            'note': forms.Textarea(attrs={'rows': 3}),
            'anno_immatricolazione': forms.NumberInput(attrs={
                'min': '1900', 
                'max': date.today().year + 1
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            # Dati Generali
            Fieldset(
                'Dati Generali del Veicolo',
                Row(
                    Column('targa', css_class='form-group col-md-4'),
                    Column('marca', css_class='form-group col-md-4'),
                    Column('modello', css_class='form-group col-md-4'),
                ),
                Row(
                    Column('anno_immatricolazione', css_class='form-group col-md-6'),
                    Column('numero_telaio', css_class='form-group col-md-6'),
                ),
            ),
            
            # Dati Tecnici
            Fieldset(
                'Dati Tecnici',
                Row(
                    Column('tipo_carburante', css_class='form-group col-md-4'),
                    Column('cilindrata', css_class='form-group col-md-4'),
                    Column('potenza', css_class='form-group col-md-4'),
                ),
            ),
            
            # Chilometraggio
            Fieldset(
                'Chilometraggio',
                Row(
                    Column('chilometri_iniziali', css_class='form-group col-md-6'),
                    Column('chilometri_attuali', css_class='form-group col-md-6'),
                ),
                HTML('<small class="form-text text-muted">I chilometri attuali devono essere maggiori o uguali a quelli iniziali</small>'),
            ),
            
            # Dati Acquisto
            Fieldset(
                'Dati di Acquisto',
                Row(
                    Column('data_acquisto', css_class='form-group col-md-6'),
                    Column('costo_acquisto', css_class='form-group col-md-6'),
                ),
            ),
            
            # Assegnazione e Stato
            Fieldset(
                'Assegnazione e Stato',
                Row(
                    Column('assegnato_a', css_class='form-group col-md-6'),
                    Column(
                        Div(
                            'attivo',
                            'disponibile',
                            css_class='form-check-container'
                        ),
                        css_class='form-group col-md-6'
                    ),
                ),
                'note',
            ),
            
            FormActions(
                Submit('submit', 'Salva Automezzo', css_class='btn btn-primary'),
            )
        )
    
    def clean(self):
        cleaned_data = super().clean()
        chilometri_iniziali = cleaned_data.get('chilometri_iniziali')
        chilometri_attuali = cleaned_data.get('chilometri_attuali')
        
        if chilometri_iniziali is not None and chilometri_attuali is not None:
            if chilometri_attuali < chilometri_iniziali:
                raise forms.ValidationError(
                    "I chilometri attuali non possono essere inferiori a quelli iniziali"
                )
        
        return cleaned_data
    
    def clean_targa(self):
        """Converte la targa in maiuscolo"""
        targa = self.cleaned_data.get('targa')
        if targa:
            return targa.upper().strip()
        return targa


class DocumentoAutomezzoForm(forms.ModelForm):
    """Form per la gestione dei documenti degli automezzi"""
    
    class Meta:
        model = DocumentoAutomezzo
        fields = [
            'tipo', 'numero_documento', 'data_rilascio', 'data_scadenza',
            'costo', 'file_documento', 'note'
        ]
        widgets = {
            'data_rilascio': DateInput(),
            'data_scadenza': DateInput(),
            'costo': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.automezzo = kwargs.pop('automezzo', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Fieldset(
                f'Documento per {self.automezzo.targa if self.automezzo else "Automezzo"}',
                Row(
                    Column('tipo', css_class='form-group col-md-6'),
                    Column('numero_documento', css_class='form-group col-md-6'),
                ),
                Row(
                    Column('data_rilascio', css_class='form-group col-md-6'),
                    Column('data_scadenza', css_class='form-group col-md-6'),
                ),
                Row(
                    Column('costo', css_class='form-group col-md-6'),
                    Column('file_documento', css_class='form-group col-md-6'),
                ),
                'note',
            ),
            FormActions(
                Submit('submit', 'Salva Documento', css_class='btn btn-primary'),
            )
        )
    
    def clean(self):
        cleaned_data = super().clean()
        data_rilascio = cleaned_data.get('data_rilascio')
        data_scadenza = cleaned_data.get('data_scadenza')
        
        if data_rilascio and data_scadenza:
            if data_scadenza <= data_rilascio:
                raise forms.ValidationError(
                    "La data di scadenza deve essere successiva alla data di rilascio"
                )
        
        return cleaned_data


class ManutenzioneForm(forms.ModelForm):
    """Form per la gestione delle manutenzioni"""
    
    class Meta:
        model = Manutenzione
        fields = [
            'tipo', 'descrizione', 'data_prevista', 'data_effettuata',
            'chilometri_manutenzione', 'costo_previsto', 'costo_effettivo',
            'completata', 'responsabile', 'note', 'file_allegato'
        ]
        widgets = {
            'data_prevista': DateInput(),
            'data_effettuata': DateInput(),
            'costo_previsto': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'costo_effettivo': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'chilometri_manutenzione': forms.NumberInput(attrs={'min': '0'}),
            'descrizione': forms.Textarea(attrs={'rows': 3}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.automezzo = kwargs.pop('automezzo', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Fieldset(
                f'Manutenzione per {self.automezzo.targa if self.automezzo else "Automezzo"}',
                Row(
                    Column('tipo', css_class='form-group col-md-6'),
                    Column('responsabile', css_class='form-group col-md-6'),
                ),
                'descrizione',
                Row(
                    Column('data_prevista', css_class='form-group col-md-6'),
                    Column('data_effettuata', css_class='form-group col-md-6'),
                ),
                Row(
                    Column('chilometri_manutenzione', css_class='form-group col-md-6'),
                    Column('completata', css_class='form-group col-md-6'),
                ),
                Row(
                    Column('costo_previsto', css_class='form-group col-md-6'),
                    Column('costo_effettivo', css_class='form-group col-md-6'),
                ),
                Row(
                    Column('file_allegato', css_class='form-group col-md-12'),
                ),
                'note',
            ),
            FormActions(
                Submit('submit', 'Salva Manutenzione', css_class='btn btn-primary'),
            )
        )
        
        # Se la manutenzione non è completata, rendi opzionali alcuni campi
        if not self.instance.pk or not self.instance.completata:
            self.fields['data_effettuata'].required = False
            self.fields['costo_effettivo'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        completata = cleaned_data.get('completata')
        data_prevista = cleaned_data.get('data_prevista')
        data_effettuata = cleaned_data.get('data_effettuata')
        
        # Se completata, deve avere la data effettuata
        if completata and not data_effettuata:
            cleaned_data['data_effettuata'] = date.today()
        
        # La data effettuata non può essere anteriore alla data prevista
        if data_prevista and data_effettuata and data_effettuata < data_prevista:
            raise forms.ValidationError(
                "La data di effettuazione non può essere anteriore alla data prevista"
            )
        
        return cleaned_data


class RifornimentoCarburanteForm(forms.ModelForm):
    """Form per la registrazione dei rifornimenti"""
    
    class Meta:
        model = RifornimentoCarburante
        fields = [
            'data_rifornimento', 'chilometri', 'litri', 'costo_totale',
            'costo_per_litro', 'distributore', 'effettuato_da', 'note'
        ]
        widgets = {
            'data_rifornimento': DateInput(),
            'litri': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'costo_totale': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'costo_per_litro': forms.NumberInput(attrs={'step': '0.001', 'min': '0'}),
            'chilometri': forms.NumberInput(attrs={'min': '0'}),
            'note': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        self.automezzo = kwargs.pop('automezzo', None)
        super().__init__(*args, **kwargs)
        
        # Imposta i chilometri attuali come valore di default
        if self.automezzo and not self.instance.pk:
            self.fields['chilometri'].initial = self.automezzo.chilometri_attuali
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                f'Rifornimento per {self.automezzo.targa if self.automezzo else "Automezzo"}',
                Row(
                    Column('data_rifornimento', css_class='form-group col-md-6'),
                    Column('chilometri', css_class='form-group col-md-6'),
                ),
                Row(
                    Column('litri', css_class='form-group col-md-4'),
                    Column('costo_totale', css_class='form-group col-md-4'),
                    Column('costo_per_litro', css_class='form-group col-md-4'),
                ),
                HTML('<small class="form-text text-muted">Il costo per litro verrà calcolato automaticamente se lasciato vuoto</small>'),
                Row(
                    Column('distributore', css_class='form-group col-md-6'),
                    Column('effettuato_da', css_class='form-group col-md-6'),
                ),
                'note',
            ),
            FormActions(
                Submit('submit', 'Salva Rifornimento', css_class='btn btn-primary'),
            )
        )
    
    def clean(self):
        cleaned_data = super().clean()
        chilometri = cleaned_data.get('chilometri')
        
        # Verifica che i chilometri non siano inferiori a quelli attuali dell'automezzo
        if self.automezzo and chilometri:
            if chilometri < self.automezzo.chilometri_attuali:
                raise forms.ValidationError(
                    f"I chilometri del rifornimento ({chilometri}) non possono essere inferiori "
                    f"ai chilometri attuali dell'automezzo ({self.automezzo.chilometri_attuali})"
                )
        
        return cleaned_data
    
    def clean_chilometri(self):
        """Validazione specifica per il campo chilometri"""
        chilometri = self.cleaned_data.get('chilometri')
        
        # Controlla che non ci siano già rifornimenti con chilometri superiori
        if self.automezzo and chilometri:
            rifornimenti_successivi = RifornimentoCarburante.objects.filter(
                automezzo=self.automezzo,
                chilometri__gt=chilometri
            )
            if self.instance.pk:
                rifornimenti_successivi = rifornimenti_successivi.exclude(pk=self.instance.pk)
            
            if rifornimenti_successivi.exists():
                raise forms.ValidationError(
                    "Esistono già rifornimenti registrati con chilometri superiori"
                )
        
        return chilometri


class EventoAutomezzoForm(forms.ModelForm):
    """Form per la gestione degli eventi degli automezzi"""
    
    class Meta:
        model = EventoAutomezzo
        fields = [
            'tipo', 'data_evento', 'chilometri', 'descrizione',
            'costo', 'risolto', 'dipendente_coinvolto', 'file_allegato', 'note'
        ]
        widgets = {
            'data_evento': DateInput(),
            'chilometri': forms.NumberInput(attrs={'min': '0'}),
            'costo': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'descrizione': forms.Textarea(attrs={'rows': 4}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.automezzo = kwargs.pop('automezzo', None)
        super().__init__(*args, **kwargs)
        
        # Imposta i chilometri attuali come valore di default
        if self.automezzo and not self.instance.pk:
            self.fields['chilometri'].initial = self.automezzo.chilometri_attuali
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Fieldset(
                f'Evento per {self.automezzo.targa if self.automezzo else "Automezzo"}',
                Row(
                    Column('tipo', css_class='form-group col-md-6'),
                    Column('data_evento', css_class='form-group col-md-6'),
                ),
                Row(
                    Column('chilometri', css_class='form-group col-md-6'),
                    Column('costo', css_class='form-group col-md-6'),
                ),
                'descrizione',
                Row(
                    Column('dipendente_coinvolto', css_class='form-group col-md-6'),
                    Column('risolto', css_class='form-group col-md-6'),
                ),
                'file_allegato',
                'note',
            ),
            FormActions(
                Submit('submit', 'Salva Evento', css_class='btn btn-primary'),
            )
        )


class AutomezzoSearchForm(forms.Form):
    """Form per la ricerca degli automezzi"""
    
    q = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Cerca per targa, marca, modello...',
            'class': 'form-control'
        })
    )
    
    tipo_carburante = forms.ModelChoiceField(
        queryset=TipoCarburante.objects.all(),
        required=False,
        empty_label="Tutti i carburanti",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    assegnato_a = forms.ModelChoiceField(
        queryset=None,  # Verrà impostato in __init__
        required=False,
        empty_label="Tutti i dipendenti",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    solo_attivi = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Importa qui per evitare import circolari
        from dipendenti.models import Dipendente
        self.fields['assegnato_a'].queryset = Dipendente.objects.filter(is_active=True)
        
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline mb-3'
        self.helper.layout = Layout(
            Row(
                Column('q', css_class='form-group col-md-4'),
                Column('tipo_carburante', css_class='form-group col-md-3'),
                Column('assegnato_a', css_class='form-group col-md-3'),
                Column('solo_attivi', css_class='form-group col-md-2'),
            ),
            FormActions(
                Submit('submit', 'Cerca', css_class='btn btn-primary'),
            )
        )


class FiltroScadenzeForm(forms.Form):
    """Form per filtrare le scadenze"""
    
    GIORNI_CHOICES = [
        (15, '15 giorni'),
        (30, '30 giorni'),
        (60, '60 giorni'),
        (90, '90 giorni'),
    ]
    
    giorni = forms.ChoiceField(
        choices=GIORNI_CHOICES,
        initial=30,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    solo_non_scaduti = forms.BooleanField(
        required=False,
        initial=True,
        label="Solo documenti non ancora scaduti",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline mb-3'
        self.helper.layout = Layout(
            Row(
                Column('giorni', css_class='form-group col-md-6'),
                Column('solo_non_scaduti', css_class='form-group col-md-6'),
            ),
            FormActions(
                Submit('submit', 'Filtra', css_class='btn btn-primary btn-sm'),
            )
        )