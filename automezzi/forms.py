from django import forms
from .models import Automezzo, Manutenzione, Rifornimento, EventoAutomezzo

class AutomezzoForm(forms.ModelForm):
    class Meta:
        model = Automezzo
        fields = [
            'targa', 'marca', 'modello', 'anno_immatricolazione', 'chilometri_attuali',
            'attivo', 'disponibile', 'bloccata', 'motivo_blocco',
            'libretto_fronte', 'libretto_retro', 'assicurazione', 'data_revisione', 'assegnato_a'
        ]
        widgets = {
            'data_revisione': forms.DateInput(attrs={'type': 'date'}),
            'motivo_blocco': forms.Textarea(attrs={'rows': 2}),
        }

class ManutenzioneForm(forms.ModelForm):
    class Meta:
        model = Manutenzione
        fields = [
            'automezzo', 'data', 'descrizione', 'costo',
            'completata', 'responsabile', 'allegati'
        ]
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'descrizione': forms.Textarea(attrs={'rows': 2}),
        }

class RifornimentoForm(forms.ModelForm):
    class Meta:
        model = Rifornimento
        fields = [
            'automezzo', 'data', 'litri', 'costo_totale',
            'chilometri', 'scontrino'
        ]
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
        }

class EventoAutomezzoForm(forms.ModelForm):
    class Meta:
        model = EventoAutomezzo
        fields = [
            'automezzo', 'tipo', 'data_evento', 'descrizione', 'costo',
            'dipendente_coinvolto', 'file_allegato', 'risolto'
        ]
        widgets = {
            'data_evento': forms.DateInput(attrs={'type': 'date'}),
            'descrizione': forms.Textarea(attrs={'rows': 2}),
        }