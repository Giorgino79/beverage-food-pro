from django import forms
from django.forms import DateTimeInput, DateInput
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, timedelta
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, HTML, Button
from crispy_forms.bootstrap import PrependedText, AppendedText, FieldWithButtons, StrictButton
from .models import Categoria, Prodotto, Ordine, Ricezione, ProdottoRicevuto, Magazzino
from anagrafica.models import Fornitore


# Widget personalizzati
class CustomDateInput(DateInput):
    input_type = 'date'
    
    def __init__(self, attrs=None):
        default_attrs = {'class': 'form-control'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class CustomDecimalInput(forms.NumberInput):
    def __init__(self, attrs=None):
        default_attrs = {'class': 'form-control', 'step': '0.01'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


# Form per Categoria
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome_categoria', 'descrizione', 'icona', 'ordinamento', 'attiva']
        widgets = {
            'nome_categoria': forms.TextInput(attrs={'class': 'form-control'}),
            'descrizione': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ordinamento': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'attiva': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Informazioni Categoria',
                Row(
                    Column('nome_categoria', css_class='col-md-8'),
                    Column('ordinamento', css_class='col-md-4'),
                ),
                'descrizione',
                Row(
                    Column('icona', css_class='col-md-6'),
                    Column('attiva', css_class='col-md-6'),
                ),
                css_class='border p-3 mb-3'
            ),
            Row(
                Column(
                    Submit('submit', 'Salva', css_class='btn btn-primary'),
                    css_class='col-12 text-end'
                )
            )
        )


# Form per Prodotto
class ProdottoForm(forms.ModelForm):
    class Meta:
        model = Prodotto
        fields = [
            'categoria', 'nome_prodotto', 'descrizione', 'ean', 'codice_interno',
            'misura', 'peso_netto', 'volume', 'aliquota_iva',
            'scorta_minima', 'scorta_massima', 'attivo'
        ]
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'nome_prodotto': forms.TextInput(attrs={'class': 'form-control'}),
            'descrizione': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ean': forms.TextInput(attrs={
                'class': 'form-control',
                'pattern': '[0-9]{13}',
                'title': 'EAN deve contenere esattamente 13 cifre'
            }),
            'codice_interno': forms.TextInput(attrs={'class': 'form-control'}),
            'misura': forms.Select(attrs={'class': 'form-select'}),
            'peso_netto': CustomDecimalInput(attrs={'step': '0.001'}),
            'volume': CustomDecimalInput(attrs={'step': '0.001'}),
            'aliquota_iva': forms.Select(attrs={'class': 'form-select'}),
            'scorta_minima': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'scorta_massima': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'attivo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Informazioni Generali',
                Row(
                    Column('categoria', css_class='col-md-6'),
                    Column('misura', css_class='col-md-6'),
                ),
                'nome_prodotto',
                'descrizione',
                css_class='border p-3 mb-3'
            ),
            Fieldset(
                'Codici Identificativi',
                Row(
                    Column('ean', css_class='col-md-6'),
                    Column('codice_interno', css_class='col-md-6'),
                ),
                css_class='border p-3 mb-3'
            ),
            Fieldset(
                'Caratteristiche Fisiche',
                Row(
                    Column(
                        PrependedText('peso_netto', 'kg'),
                        css_class='col-md-4'
                    ),
                    Column(
                        PrependedText('volume', 'L'),
                        css_class='col-md-4'
                    ),
                    Column('aliquota_iva', css_class='col-md-4'),
                ),
                css_class='border p-3 mb-3'
            ),
            Fieldset(
                'Gestione Scorte',
                Row(
                    Column('scorta_minima', css_class='col-md-4'),
                    Column('scorta_massima', css_class='col-md-4'),
                    Column('attivo', css_class='col-md-4'),
                ),
                css_class='border p-3 mb-3'
            ),
            Row(
                Column(
                    Submit('submit', 'Salva Prodotto', css_class='btn btn-primary'),
                    css_class='col-12 text-end'
                )
            )
        )

    def clean_ean(self):
        ean = self.cleaned_data.get('ean')
        if ean:
            # Rimuovi spazi e assicurati che sia numerico
            ean = ean.replace(' ', '').strip()
            if not ean.isdigit():
                raise ValidationError("EAN deve contenere solo cifre")
            if len(ean) != 13:
                raise ValidationError("EAN deve essere di esattamente 13 cifre")
        return ean

    def clean(self):
        cleaned_data = super().clean()
        scorta_min = cleaned_data.get('scorta_minima')
        scorta_max = cleaned_data.get('scorta_massima')
        
        if scorta_min and scorta_max and scorta_min > scorta_max:
            raise ValidationError("La scorta minima non può essere maggiore di quella massima")
        
        return cleaned_data


# Form per Ordine
class OrdineForm(forms.ModelForm):
    class Meta:
        model = Ordine
        fields = [
            'prodotto', 'fornitore', 'misura', 'pezzi_per_confezione',
            'quantita_ordinata', 'prezzo_unitario_ordine', 'sconto_percentuale',
            'data_arrivo_previsto', 'note_interne', 'note_fornitore'
        ]
        widgets = {
            'prodotto': forms.Select(attrs={'class': 'form-select'}),
            'fornitore': forms.Select(attrs={'class': 'form-select'}),
            'misura': forms.Select(attrs={'class': 'form-select'}),
            'pezzi_per_confezione': CustomDecimalInput(),
            'quantita_ordinata': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'prezzo_unitario_ordine': CustomDecimalInput(),
            'sconto_percentuale': CustomDecimalInput(attrs={'min': 0, 'max': 100}),
            'data_arrivo_previsto': CustomDateInput(),
            'note_interne': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'note_fornitore': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtra prodotti attivi
        self.fields['prodotto'].queryset = Prodotto.objects.filter(attivo=True)
        
        # Filtra fornitori attivi
        self.fields['fornitore'].queryset = Fornitore.objects.filter(attivo=True)
        
        # Imposta data arrivo previsto default (7 giorni da oggi)
        if not self.instance.pk:
            self.fields['data_arrivo_previsto'].initial = date.today() + timedelta(days=7)
        
        # Configura il campo pezzi_per_confezione
        if self.instance.pk and self.instance.misura != Ordine.Misura.CONFEZIONE:
            self.fields['pezzi_per_confezione'].widget = forms.HiddenInput()
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Dettagli Ordine',
                Row(
                    Column('prodotto', css_class='col-md-6'),
                    Column('fornitore', css_class='col-md-6'),
                ),
                Row(
                    Column('misura', css_class='col-md-4'),
                    Column('pezzi_per_confezione', css_class='col-md-4'),
                    Column('quantita_ordinata', css_class='col-md-4'),
                ),
                css_class='border p-3 mb-3'
            ),
            Fieldset(
                'Prezzi e Condizioni',
                Row(
                    Column(
                        PrependedText('prezzo_unitario_ordine', '€'),
                        css_class='col-md-6'
                    ),
                    Column(
                        AppendedText('sconto_percentuale', '%'),
                        css_class='col-md-6'
                    ),
                ),
                'data_arrivo_previsto',
                css_class='border p-3 mb-3'
            ),
            Fieldset(
                'Note',
                'note_interne',
                'note_fornitore',
                css_class='border p-3 mb-3'
            ),
            # Area di calcolo prezzi (solo visualizzazione, aggiornata via JS)
            HTML('''
                <div class="border p-3 mb-3" id="price-calculation" style="display: none;">
                    <h6>Calcolo Prezzi</h6>
                    <div class="row">
                        <div class="col-md-4">
                            <label>Prezzo Scontato Unitario:</label>
                            <span id="prezzo-scontato" class="form-control-plaintext">€ 0.00</span>
                        </div>
                        <div class="col-md-4">
                            <label>Totale (senza IVA):</label>
                            <span id="totale-ordine" class="form-control-plaintext">€ 0.00</span>
                        </div>
                        <div class="col-md-4">
                            <label>Totale con IVA:</label>
                            <span id="totale-ivato" class="form-control-plaintext">€ 0.00</span>
                        </div>
                    </div>
                </div>
            '''),
            Row(
                Column(
                    Submit('submit', 'Salva Ordine', css_class='btn btn-primary me-2'),
                    HTML('''
                        {% if object.pk and object.status == 'bozza' %}
                            <button type="submit" name="invia_ordine" value="1" class="btn btn-success">
                                Invia Ordine
                            </button>
                        {% endif %}
                    '''),
                    css_class='col-12 text-end'
                )
            )
        )

    def clean_quantita_ordinata(self):
        quantita = self.cleaned_data.get('quantita_ordinata')
        if quantita and quantita <= 0:
            raise ValidationError("La quantità deve essere maggiore di zero")
        return quantita

    def clean_prezzo_unitario_ordine(self):
        prezzo = self.cleaned_data.get('prezzo_unitario_ordine')
        if prezzo and prezzo <= 0:
            raise ValidationError("Il prezzo deve essere maggiore di zero")
        return prezzo

    def save(self, commit=True):
        ordine = super().save(commit=False)
        if self.user:
            ordine.creato_da = self.user
        if commit:
            ordine.save()
        return ordine


# Form per aggiornamento stato ordine
class AggiornaStatoOrdineForm(forms.ModelForm):
    class Meta:
        model = Ordine
        fields = ['status', 'data_invio_ordine', 'data_arrivo_previsto', 'note_interne']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'data_invio_ordine': CustomDateInput(),
            'data_arrivo_previsto': CustomDateInput(),
            'note_interne': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Rimuovi status che non possono essere selezionati manualmente
        status_choices = list(Ordine.StatusOrdine.choices)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Aggiorna Stato Ordine',
                'status',
                Row(
                    Column('data_invio_ordine', css_class='col-md-6'),
                    Column('data_arrivo_previsto', css_class='col-md-6'),
                ),
                'note_interne',
                css_class='border p-3 mb-3'
            ),
            Row(
                Column(
                    Submit('submit', 'Aggiorna', css_class='btn btn-primary'),
                    css_class='col-12 text-end'
                )
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        data_invio = cleaned_data.get('data_invio_ordine')
        
        # Se status è INVIATO o superiore, richiedi data invio
        status_inviati = [
            Ordine.StatusOrdine.INVIATO,
            Ordine.StatusOrdine.CONFERMATO,
            Ordine.StatusOrdine.IN_PRODUZIONE,
            Ordine.StatusOrdine.SPEDITO,
            Ordine.StatusOrdine.IN_TRANSITO,
            Ordine.StatusOrdine.RICEVUTO,
            Ordine.StatusOrdine.COMPLETATO
        ]
        
        if status in status_inviati and not data_invio:
            raise ValidationError("La data di invio è obbligatoria per questo stato")
        
        return cleaned_data


# Form per Ricezione
class RicezioneForm(forms.ModelForm):
    class Meta:
        model = Ricezione
        fields = ['data_ricezione', 'note']
        widgets = {
            'data_ricezione': CustomDateInput(),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.ordine = kwargs.pop('ordine', None)
        super().__init__(*args, **kwargs)
        
        if not self.instance.pk:
            self.fields['data_ricezione'].initial = date.today()
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                f'Ricezione Ordine {self.ordine.numero_ordine if self.ordine else ""}',
                HTML(f'''
                    <div class="alert alert-info">
                        <strong>Prodotto:</strong> {self.ordine.prodotto.nome_prodotto if self.ordine else ""}<br>
                        <strong>Quantità Ordinata:</strong> {self.ordine.quantita_ordinata if self.ordine else ""} {self.ordine.get_misura_display() if self.ordine else ""}
                    </div>
                ''') if self.ordine else '',
                'data_ricezione',
                'note',
                css_class='border p-3 mb-3'
            ),
            Row(
                Column(
                    Submit('submit', 'Conferma Ricezione', css_class='btn btn-success'),
                    css_class='col-12 text-end'
                )
            )
        )


# Form per Prodotto Ricevuto
class ProdottoRicevutoForm(forms.ModelForm):
    class Meta:
        model = ProdottoRicevuto
        fields = ['quantita_ricevuta', 'data_scadenza', 'numero_lotto', 'note']
        widgets = {
            'quantita_ricevuta': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'data_scadenza': CustomDateInput(),
            'numero_lotto': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        self.ordine = kwargs.pop('ordine', None)
        super().__init__(*args, **kwargs)
        
        # Pre-imposta la quantità ordinata
        if self.ordine and not self.instance.pk:
            self.fields['quantita_ricevuta'].initial = self.ordine.quantita_ordinata
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('quantita_ricevuta', css_class='col-md-6'),
                Column('data_scadenza', css_class='col-md-6'),
            ),
            Row(
                Column('numero_lotto', css_class='col-md-6'),
                Column('note', css_class='col-md-6'),
            ),
        )


# Form per ricerca ordini
class OrdineSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cerca per numero ordine, prodotto, fornitore...'
        })
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'Tutti gli stati')] + list(Ordine.StatusOrdine.choices),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    fornitore = forms.ModelChoiceField(
        required=False,
        queryset=Fornitore.objects.filter(attivo=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Tutti i fornitori"
    )
    categoria = forms.ModelChoiceField(
        required=False,
        queryset=Categoria.objects.filter(attiva=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Tutte le categorie"
    )
    data_da = forms.DateField(
        required=False,
        widget=CustomDateInput()
    )
    data_a = forms.DateField(
        required=False,
        widget=CustomDateInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.layout = Layout(
            Row(
                Column('q', css_class='col-md-4'),
                Column('status', css_class='col-md-4'),
                Column('fornitore', css_class='col-md-4'),
            ),
            Row(
                Column('categoria', css_class='col-md-4'),
                Column('data_da', css_class='col-md-4'),
                Column('data_a', css_class='col-md-4'),
            ),
            Row(
                Column(
                    Submit('submit', 'Filtra', css_class='btn btn-primary me-2'),
                    Button('reset', 'Reset', css_class='btn btn-secondary'),
                    css_class='col-12 text-end'
                )
            )
        )


# Form per gestione magazzino
class MagazzinoForm(forms.ModelForm):
    class Meta:
        model = Magazzino
        fields = [
            'prodotto', 'quantita_in_magazzino', 'data_scadenza', 'numero_lotto',
            'costo_unitario', 'settore', 'scaffale', 'piano'
        ]
        widgets = {
            'prodotto': forms.Select(attrs={'class': 'form-select'}),
            'quantita_in_magazzino': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'data_scadenza': CustomDateInput(),
            'numero_lotto': forms.TextInput(attrs={'class': 'form-control'}),
            'costo_unitario': CustomDecimalInput(),
            'settore': forms.TextInput(attrs={'class': 'form-control'}),
            'scaffale': forms.TextInput(attrs={'class': 'form-control'}),
            'piano': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['prodotto'].queryset = Prodotto.objects.filter(attivo=True)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Dettagli Prodotto',
                'prodotto',
                Row(
                    Column('quantita_in_magazzino', css_class='col-md-6'),
                    Column('costo_unitario', css_class='col-md-6'),
                ),
                css_class='border p-3 mb-3'
            ),
            Fieldset(
                'Tracciabilità',
                Row(
                    Column('data_scadenza', css_class='col-md-6'),
                    Column('numero_lotto', css_class='col-md-6'),
                ),
                css_class='border p-3 mb-3'
            ),
            Fieldset(
                'Posizione in Magazzino',
                Row(
                    Column('settore', css_class='col-md-4'),
                    Column('scaffale', css_class='col-md-4'),
                    Column('piano', css_class='col-md-4'),
                ),
                css_class='border p-3 mb-3'
            ),
            Row(
                Column(
                    Submit('submit', 'Salva', css_class='btn btn-primary'),
                    css_class='col-12 text-end'
                )
            )
        )


# Form per movimenti di magazzino (carico/scarico)
class MovimentoMagazzinoForm(forms.Form):
    TIPO_MOVIMENTO_CHOICES = [
        ('carico', 'Carico'),
        ('scarico', 'Scarico'),
        ('inventario', 'Correzione Inventario'),
    ]
    
    tipo_movimento = forms.ChoiceField(
        choices=TIPO_MOVIMENTO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    quantita = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    motivo = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        help_text="Specificare il motivo del movimento"
    )

    def __init__(self, *args, **kwargs):
        self.magazzino_item = kwargs.pop('magazzino_item', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                f'Movimento per {self.magazzino_item.prodotto.nome_prodotto if self.magazzino_item else ""}',
                HTML(f'''
                    <div class="alert alert-info">
                        <strong>Quantità Attuale:</strong> {self.magazzino_item.quantita_in_magazzino if self.magazzino_item else 0}
                    </div>
                ''') if self.magazzino_item else '',
                'tipo_movimento',
                'quantita',
                'motivo',
                css_class='border p-3 mb-3'
            ),
            Row(
                Column(
                    Submit('submit', 'Conferma Movimento', css_class='btn btn-primary'),
                    css_class='col-12 text-end'
                )
            )
        )

    def clean_quantita(self):
        quantita = self.cleaned_data.get('quantita')
        tipo_movimento = self.cleaned_data.get('tipo_movimento')
        
        if tipo_movimento == 'scarico' and self.magazzino_item:
            if quantita > self.magazzino_item.quantita_in_magazzino:
                raise ValidationError(
                    f"Quantità non sufficiente. Disponibile: {self.magazzino_item.quantita_in_magazzino}"
                )
        
        return quantita


# Form per filtri magazzino
class MagazzinoFilterForm(forms.Form):
    prodotto = forms.ModelChoiceField(
        required=False,
        queryset=Prodotto.objects.filter(attivo=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Tutti i prodotti"
    )
    categoria = forms.ModelChoiceField(
        required=False,
        queryset=Categoria.objects.filter(attiva=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Tutte le categorie"
    )
    in_scadenza = forms.IntegerField(
        required=False,
        initial=30,
        min_value=1,
        max_value=365,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Giorni entro cui il prodotto scade"
    )
    scorte_basse = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    solo_disponibili = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.layout = Layout(
            Row(
                Column('prodotto', css_class='col-md-3'),
                Column('categoria', css_class='col-md-3'),
                Column('in_scadenza', css_class='col-md-3'),
                Column(
                    HTML('<label class="form-label">&nbsp;</label>'),
                    Submit('submit', 'Filtra', css_class='btn btn-primary d-block'),
                    css_class='col-md-3'
                ),
            ),
            Row(
                Column('scorte_basse', css_class='col-md-6'),
                Column('solo_disponibili', css_class='col-md-6'),
            ),
        )


# Form inline per multiple ricezioni prodotti
class ProdottoRicevutoInlineFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.ordine = kwargs.pop('ordine', None)
        super().__init__(*args, **kwargs)
    
    def _construct_form(self, i, **kwargs):
        form = super()._construct_form(i, **kwargs)
        if self.ordine and not form.instance.pk:
            form.fields['quantita_ricevuta'].initial = self.ordine.quantita_ordinata
        return form


# Helper per formset di prodotti ricevuti
ProdottoRicevutoFormSet = forms.inlineformset_factory(
    Ricezione,
    ProdottoRicevuto,
    form=ProdottoRicevutoForm,
    formset=ProdottoRicevutoInlineFormSet,
    extra=1,
    can_delete=True
)


# Form per export dati
class ExportOrdiniForm(forms.Form):
    FORMATO_CHOICES = [
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('pdf', 'PDF'),
    ]
    
    formato = forms.ChoiceField(
        choices=FORMATO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    data_da = forms.DateField(
        required=False,
        widget=CustomDateInput()
    )
    data_a = forms.DateField(
        required=False,
        widget=CustomDateInput()
    )
    status = forms.MultipleChoiceField(
        required=False,
        choices=Ordine.StatusOrdine.choices,
        widget=forms.CheckboxSelectMultiple()
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Default: ultimi 30 giorni
        if not self.data:
            self.fields['data_da'].initial = date.today() - timedelta(days=30)
            self.fields['data_a'].initial = date.today()
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Configurazione Export',
                'formato',
                Row(
                    Column('data_da', css_class='col-md-6'),
                    Column('data_a', css_class='col-md-6'),
                ),
               'status',
               css_class='border p-3 mb-3'
           ),
           Row(
               Column(
                   Submit('submit', 'Esporta', css_class='btn btn-success'),
                   css_class='col-12 text-end'
               )
           )
       )


# Form per report e statistiche
class ReportOrdiniForm(forms.Form):
   TIPO_REPORT_CHOICES = [
       ('ordini_per_fornitore', 'Ordini per Fornitore'),
       ('prodotti_piu_ordinati', 'Prodotti Più Ordinati'),
       ('trend_ordini', 'Trend Ordini nel Tempo'),
       ('costi_per_categoria', 'Costi per Categoria'),
       ('analisi_tempi_consegna', 'Analisi Tempi di Consegna'),
   ]
   
   tipo_report = forms.ChoiceField(
       choices=TIPO_REPORT_CHOICES,
       widget=forms.Select(attrs={'class': 'form-select'})
   )
   data_da = forms.DateField(
       widget=CustomDateInput()
   )
   data_a = forms.DateField(
       widget=CustomDateInput()
   )
   fornitore = forms.ModelChoiceField(
       required=False,
       queryset=Fornitore.objects.filter(attivo=True),
       widget=forms.Select(attrs={'class': 'form-select'}),
       empty_label="Tutti i fornitori"
   )
   categoria = forms.ModelChoiceField(
       required=False,
       queryset=Categoria.objects.filter(attiva=True),
       widget=forms.Select(attrs={'class': 'form-select'}),
       empty_label="Tutte le categorie"
   )
   
   def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)
       # Default: ultimi 3 mesi
       if not self.data:
           self.fields['data_da'].initial = date.today() - timedelta(days=90)
           self.fields['data_a'].initial = date.today()
       
       self.helper = FormHelper()
       self.helper.layout = Layout(
           Fieldset(
               'Parametri Report',
               'tipo_report',
               Row(
                   Column('data_da', css_class='col-md-6'),
                   Column('data_a', css_class='col-md-6'),
               ),
               Row(
                   Column('fornitore', css_class='col-md-6'),
                   Column('categoria', css_class='col-md-6'),
               ),
               css_class='border p-3 mb-3'
           ),
           Row(
               Column(
                   Submit('submit', 'Genera Report', css_class='btn btn-primary'),
                   css_class='col-12 text-end'
               )
           )
       )


# Form per configurazione alert magazzino
class AlertMagazzinoForm(forms.Form):
   giorni_scadenza = forms.IntegerField(
       initial=30,
       min_value=1,
       max_value=365,
       widget=forms.NumberInput(attrs={'class': 'form-control'}),
       help_text="Alert per prodotti che scadono entro N giorni"
   )
   soglia_scorta_minima = forms.BooleanField(
       required=False,
       initial=True,
       widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
       help_text="Alert quando la scorta scende sotto il minimo"
   )
   email_notifiche = forms.BooleanField(
       required=False,
       widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
       help_text="Invia notifiche via email"
   )
   
   def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)
       self.helper = FormHelper()
       self.helper.layout = Layout(
           Fieldset(
               'Configurazione Alert Magazzino',
               'giorni_scadenza',
               'soglia_scorta_minima',
               'email_notifiche',
               css_class='border p-3 mb-3'
           ),
           Row(
               Column(
                   Submit('submit', 'Salva Configurazione', css_class='btn btn-primary'),
                   css_class='col-12 text-end'
               )
           )
       )


# Form per inventario fisico
class InventarioFisicoForm(forms.Form):
   prodotto = forms.ModelChoiceField(
       queryset=Prodotto.objects.filter(attivo=True),
       widget=forms.Select(attrs={'class': 'form-select'})
   )
   quantita_contata = forms.IntegerField(
       min_value=0,
       widget=forms.NumberInput(attrs={'class': 'form-control'})
   )
   data_inventario = forms.DateField(
       initial=date.today,
       widget=CustomDateInput()
   )
   note = forms.CharField(
       required=False,
       widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
       help_text="Note sull'inventario o discrepanze trovate"
   )
   
   def __init__(self, *args, **kwargs):
       self.magazzino_item = kwargs.pop('magazzino_item', None)
       super().__init__(*args, **kwargs)
       
       if self.magazzino_item:
           self.fields['prodotto'].initial = self.magazzino_item.prodotto
           self.fields['prodotto'].widget.attrs['readonly'] = True
       
       self.helper = FormHelper()
       self.helper.layout = Layout(
           Fieldset(
               'Inventario Fisico',
               HTML(f'''
                   <div class="alert alert-info">
                       <strong>Quantità Sistema:</strong> {self.magazzino_item.quantita_in_magazzino if self.magazzino_item else 0}<br>
                       <strong>Prodotto:</strong> {self.magazzino_item.prodotto.nome_prodotto if self.magazzino_item else ""}
                   </div>
               ''') if self.magazzino_item else '',
               'prodotto' if not self.magazzino_item else HTML(''),
               Row(
                   Column('quantita_contata', css_class='col-md-6'),
                   Column('data_inventario', css_class='col-md-6'),
               ),
               'note',
               css_class='border p-3 mb-3'
           ),
           Row(
               Column(
                   Submit('submit', 'Conferma Inventario', css_class='btn btn-primary'),
                   css_class='col-12 text-end'
               )
           )
       )


# Form per pianificazione ordini automatici
class OrdineAutomaticoForm(forms.ModelForm):
   class Meta:
       model = Prodotto
       fields = ['scorta_minima', 'scorta_massima']
       widgets = {
           'scorta_minima': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
           'scorta_massima': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
       }
   
   fornitore_preferito = forms.ModelChoiceField(
       queryset=Fornitore.objects.filter(attivo=True),
       widget=forms.Select(attrs={'class': 'form-select'}),
       help_text="Fornitore preferito per ordini automatici"
   )
   quantita_ordine_automatico = forms.IntegerField(
       min_value=1,
       widget=forms.NumberInput(attrs={'class': 'form-control'}),
       help_text="Quantità da ordinare automaticamente"
   )
   abilita_ordine_automatico = forms.BooleanField(
       required=False,
       widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
       help_text="Abilita ordini automatici per questo prodotto"
   )
   
   def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)
       self.helper = FormHelper()
       self.helper.layout = Layout(
           Fieldset(
               f'Ordine Automatico - {self.instance.nome_prodotto if self.instance else ""}',
               Row(
                   Column('scorta_minima', css_class='col-md-6'),
                   Column('scorta_massima', css_class='col-md-6'),
               ),
               'fornitore_preferito',
               Row(
                   Column('quantita_ordine_automatico', css_class='col-md-6'),
                   Column('abilita_ordine_automatico', css_class='col-md-6'),
               ),
               css_class='border p-3 mb-3'
           ),
           Row(
               Column(
                   Submit('submit', 'Salva Configurazione', css_class='btn btn-primary'),
                   css_class='col-12 text-end'
               )
           )
       )

   def clean(self):
       cleaned_data = super().clean()
       scorta_min = cleaned_data.get('scorta_minima')
       scorta_max = cleaned_data.get('scorta_massima')
       quantita_ordine = cleaned_data.get('quantita_ordine_automatico')
       
       if scorta_min and scorta_max and scorta_min >= scorta_max:
           raise ValidationError("La scorta minima deve essere inferiore alla scorta massima")
       
       if quantita_ordine and scorta_max and quantita_ordine > scorta_max:
           self.add_error('quantita_ordine_automatico', 
                         "La quantità di ordine automatico non dovrebbe superare la scorta massima")
       
       return cleaned_data


# Form di conferma per azioni bulk
class BulkActionForm(forms.Form):
   AZIONI_CHOICES = [
       ('', 'Seleziona azione'),
       ('cambia_status', 'Cambia Stato'),
       ('elimina', 'Elimina Selezionati'),
       ('esporta', 'Esporta Selezionati'),
       ('invia_email', 'Invia Email'),
   ]
   
   azione = forms.ChoiceField(
       choices=AZIONI_CHOICES,
       widget=forms.Select(attrs={'class': 'form-select'})
   )
   nuovo_status = forms.ChoiceField(
       required=False,
       choices=[('', 'Seleziona nuovo stato')] + list(Ordine.StatusOrdine.choices),
       widget=forms.Select(attrs={'class': 'form-select'})
   )
   conferma = forms.BooleanField(
       widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
       help_text="Confermo di voler eseguire questa azione"
   )
   
   def __init__(self, *args, **kwargs):
       self.selected_count = kwargs.pop('selected_count', 0)
       super().__init__(*args, **kwargs)
       
       self.helper = FormHelper()
       self.helper.layout = Layout(
           Fieldset(
               f'Azione Bulk su {self.selected_count} elementi',
               HTML(f'''
                   <div class="alert alert-warning">
                       <i class="fas fa-exclamation-triangle"></i>
                       Stai per eseguire un'azione su <strong>{self.selected_count}</strong> elementi.
                       Questa operazione non può essere annullata.
                   </div>
               '''),
               'azione',
               'nuovo_status',
               'conferma',
               css_class='border p-3 mb-3'
           ),
           Row(
               Column(
                   Button('cancel', 'Annulla', css_class='btn btn-secondary me-2'),
                   Submit('submit', 'Esegui Azione', css_class='btn btn-danger'),
                   css_class='col-12 text-end'
               )
           )
       )

   def clean(self):
       cleaned_data = super().clean()
       azione = cleaned_data.get('azione')
       conferma = cleaned_data.get('conferma')
       
       if not conferma:
           raise ValidationError("Devi confermare l'azione per procedere")
       
       if azione == 'cambia_status' and not cleaned_data.get('nuovo_status'):
           raise ValidationError("Seleziona il nuovo stato per continuare")
       
       return cleaned_data


# Form per configurazione notifiche
class NotificheConfigForm(forms.Form):
   email_scadenze = forms.BooleanField(
       required=False,
       widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
       help_text="Ricevi email per scadenze documenti/prodotti"
   )
   email_scorte_basse = forms.BooleanField(
       required=False,
       widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
       help_text="Ricevi email per scorte sotto la soglia minima"
   )
   email_ordini_ritardo = forms.BooleanField(
       required=False,
       widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
       help_text="Ricevi email per ordini in ritardo"
   )
   email_ordini_ricevuti = forms.BooleanField(
       required=False,
       widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
       help_text="Ricevi email quando un ordine viene ricevuto"
   )
   frequenza_notifiche = forms.ChoiceField(
       choices=[
           ('daily', 'Giornaliera'),
           ('weekly', 'Settimanale'),
           ('immediate', 'Immediata'),
       ],
       widget=forms.Select(attrs={'class': 'form-select'})
   )
   
   def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)
       self.helper = FormHelper()
       self.helper.layout = Layout(
           Fieldset(
               'Configurazione Notifiche Email',
               'email_scadenze',
               'email_scorte_basse',
               'email_ordini_ritardo',
               'email_ordini_ricevuti',
               'frequenza_notifiche',
               css_class='border p-3 mb-3'
           ),
           Row(
               Column(
                   Submit('submit', 'Salva Configurazione', css_class='btn btn-primary'),
                   css_class='col-12 text-end'
               )
           )
       )


# Form per quick order (ordine rapido)
class QuickOrderForm(forms.Form):
   prodotto = forms.ModelChoiceField(
       queryset=Prodotto.objects.filter(attivo=True),
       widget=forms.Select(attrs={'class': 'form-select'})
   )
   fornitore = forms.ModelChoiceField(
       queryset=Fornitore.objects.filter(attivo=True),
       widget=forms.Select(attrs={'class': 'form-select'})
   )
   quantita = forms.IntegerField(
       min_value=1,
       widget=forms.NumberInput(attrs={'class': 'form-control'})
   )
   prezzo_unitario = forms.DecimalField(
       max_digits=10,
       decimal_places=2,
       widget=CustomDecimalInput()
   )
   data_arrivo_previsto = forms.DateField(
       widget=CustomDateInput(),
       initial=lambda: date.today() + timedelta(days=7)
   )
   
   def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)
       self.helper = FormHelper()
       self.helper.layout = Layout(
           Fieldset(
               'Ordine Rapido',
               Row(
                   Column('prodotto', css_class='col-md-6'),
                   Column('fornitore', css_class='col-md-6'),
               ),
               Row(
                   Column('quantita', css_class='col-md-4'),
                   Column('prezzo_unitario', css_class='col-md-4'),
                   Column('data_arrivo_previsto', css_class='col-md-4'),
               ),
               css_class='border p-3 mb-3'
           ),
           Row(
               Column(
                   Submit('submit', 'Crea Ordine', css_class='btn btn-success'),
                   css_class='col-12 text-end'
               )
           )
       )
   
   def clean_data_arrivo_previsto(self):
       data_arrivo = self.cleaned_data.get('data_arrivo_previsto')
       if data_arrivo and data_arrivo <= date.today():
           raise ValidationError("La data di arrivo deve essere futura")
       return data_arrivo