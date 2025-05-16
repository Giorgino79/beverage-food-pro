from django import forms
from .models import *
from decimal import Decimal, InvalidOperation

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome_categoria',  'icona']
        widgets = {
            'nome_categoria': forms.TextInput(attrs={'class': 'form-control'}),
            'icona': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ProdottoForm(forms.ModelForm):
    class Meta:
        model = Prodotto
        fields = ['categoria', 'nome_prodotto', 'ean', 'misura', 'aliquota_iva']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'nome_prodotto': forms.TextInput(attrs={'class': 'form-control'}),
            'ean': forms.NumberInput(attrs={'class': 'form-control'}),
            'misura': forms.Select(attrs={'class': 'form-control'}),
            'aliquota_iva': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['aliquota_iva'].choices = Prodotto.Aliquota.choices


class OrdineForm(forms.ModelForm):
    data_invio_ordine = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), required=False)
    data_arrivo_previsto = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), required=False)
    prezzo_totale_ordine = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.HiddenInput(), initial=0.00)
    totale_ordine_ivato = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.HiddenInput(), initial=0.00)

    class Meta:
        model = Ordine
        fields = ['prodotto', 'fornitore', 'misura', 'pezzi_per_confezione', 'quantita_ordinata', 'prezzo_unitario_ordine', 'data_invio_ordine', 'data_arrivo_previsto']
        widgets = {
            'prodotto': forms.Select(attrs={'class': 'form-control'}),
            'fornitore': forms.Select(attrs={'class': 'form-control'}),
            'misura': forms.Select(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'pezzi_per_confezione': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}), # Modificato in NumberInput per FloatField
            'quantita_ordinata': forms.NumberInput(attrs={'class': 'form-control'}),
            'prezzo_unitario_ordine': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'pezzi_per_confezione': 'Pezzi per Confezione', # Aggiornata la label
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'prodotto' in self.data:
            try:
                prodotto_id = int(self.data['prodotto'])
                prodotto = Prodotto.objects.get(pk=prodotto_id)
                if prodotto.misura == Prodotto.Misura.confezione:
                    self.fields['pezzi_per_confezione'].required = True # Reso sempre richiesto se la misura è confezione
                else:
                    self.fields['pezzi_per_confezione'].required = False
                    self.fields['pezzi_per_confezione'].initial = 1.0 # Imposta a 1 per le altre misure
                self.fields['misura'].initial = prodotto.get_misura_display()
            except (ValueError, Prodotto.DoesNotExist):
                pass
        elif self.instance.pk and self.instance.prodotto:
            prodotto = self.instance.prodotto
            self.fields['misura'].initial = prodotto.get_misura_display()

        if not self.instance.pk:
            self.fields['prezzo_totale_ordine'].initial = 0.00
            self.fields['totale_ordine_ivato'].initial = 0.00

    def clean(self):
        cleaned_data = super().clean()
        prodotto = cleaned_data.get('prodotto')
        quantita_ordinata = cleaned_data.get('quantita_ordinata')
        pezzi_per_confezione = cleaned_data.get('pezzi_per_confezione')
        prezzo_unitario_ordine = cleaned_data.get('prezzo_unitario_ordine')

        prezzo_totale = Decimal('0.00')
        if prodotto and quantita_ordinata is not None and prezzo_unitario_ordine is not None:
            if prodotto.misura == Prodotto.Misura.confezione and pezzi_per_confezione is not None:
                try:
                    pezzi_per_confezione_decimal = Decimal(str(pezzi_per_confezione))
                    prezzo_totale = prezzo_unitario_ordine * pezzi_per_confezione_decimal * quantita_ordinata
                except InvalidOperation:
                    raise forms.ValidationError("Inserisci un numero valido per i pezzi per confezione.")
            elif prodotto.misura != Prodotto.Misura.confezione:
                prezzo_totale = prezzo_unitario_ordine * quantita_ordinata
                cleaned_data['pezzi_per_confezione'] = Decimal('1.0')

            aliquota_iva_numerica = prodotto.get_aliquota_iva_numerica()
            if not isinstance(aliquota_iva_numerica, Decimal):
                aliquota_iva_decimal = Decimal(str(aliquota_iva_numerica)) # Converti qui se non è Decimal
            else:
                aliquota_iva_decimal = aliquota_iva_numerica

            cleaned_data['prezzo_totale_ordine'] = prezzo_totale
            cleaned_data['totale_ordine_ivato'] = prezzo_totale * (Decimal('1.0') + aliquota_iva_decimal)

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


class RicezioneForm(forms.ModelForm):
    class Meta:
        model = Ricezione
        fields = ['ordine', 'note']
        widgets = {
            'ordine': forms.Select(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control'}),
        }


class ProdottoRicevutoForm(forms.ModelForm):
    class Meta:
        model = ProdottoRicevuto
        fields = ['prodotto', 'quantita_ricevuta', 'data_scadenza']
        widgets = {
            'prodotto': forms.Select(attrs={'class': 'form-control'}),
            'quantita_ricevuta': forms.NumberInput(attrs={'class': 'form-control'}),
            'data_scadenza': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        