from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import Messaggio, Promemoria
from dipendenti.models import Dipendente

class MessaggioForm(forms.ModelForm):
    """Form per l'invio di messaggi"""
    class Meta:
        model = Messaggio
        fields = ['destinatario', 'testo', 'allegato']
        widgets = {
            'testo': forms.Textarea(attrs={'rows': 3, 'class': 'auto-resize'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtriamo i possibili destinatari (tutti i dipendenti attivi tranne l'utente corrente)
        if self.user:
            self.fields['destinatario'].queryset = Dipendente.objects.filter(
                is_active=True
            ).exclude(id=self.user.id)
            
            # Se la vista ha specificato un destinatario, impostiamolo come valore iniziale
            destinatario_id = None
            if args and 'destinatario' in args[0]:
                try:
                    destinatario_id = int(args[0].get('destinatario'))
                except (ValueError, TypeError):
                    pass
            
            if destinatario_id:
                self.fields['destinatario'].initial = destinatario_id


class PromemoriaForm(forms.ModelForm):
    """Form per i promemoria"""
    class Meta:
        model = Promemoria
        fields = [
            'titolo', 'descrizione', 'data_scadenza', 'completato', 
            'data_completamento', 'priorita', 'assegnato_a'
        ]
        widgets = {
            'data_scadenza': forms.DateInput(attrs={'type': 'date'}),
            'data_completamento': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'descrizione': forms.Textarea(attrs={'rows': 4, 'class': 'auto-resize'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Limita le scelte per assegnato_a in base ai permessi dell'utente
        if self.user:
            if self.user.is_staff or self.user.is_superuser or (hasattr(self.user, 'livello') and 
                self.user.livello in [Dipendente.Autorizzazioni.totale, Dipendente.Autorizzazioni.contabile]):
                # Admin, superuser e utenti con livello alto possono assegnare a chiunque
                self.fields['assegnato_a'].queryset = Dipendente.objects.filter(is_active=True)
            else:
                # Gli altri possono assegnare solo a se stessi
                self.fields['assegnato_a'].queryset = Dipendente.objects.filter(id=self.user.id)
                self.fields['assegnato_a'].initial = self.user
                self.fields['assegnato_a'].widget.attrs['disabled'] = 'disabled'
    
    def clean(self):
        cleaned_data = super().clean()
        completato = cleaned_data.get('completato')
        data_completamento = cleaned_data.get('data_completamento')
        
        # Se marcato come completato ma senza data, imposta la data attuale
        if completato and not data_completamento:
            cleaned_data['data_completamento'] = timezone.now()
        
        # Se non è completato, assicuriamoci che la data di completamento sia None
        if not completato:
            cleaned_data['data_completamento'] = None
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Se è un nuovo promemoria, imposta il creatore
        if not instance.pk and self.user:
            instance.creato_da = self.user
        
        # Se è disabilitato il campo assegnato_a, impostiamo manualmente il valore
        if 'assegnato_a' in self.fields and hasattr(self.fields['assegnato_a'].widget, 'attrs') and self.fields['assegnato_a'].widget.attrs.get('disabled'):
            instance.assegnato_a = self.user
        
        if commit:
            instance.save()
        
        return instance


class MensilitaForm(forms.Form):
    """Form per la selezione del mese e dell'anno per il report"""
    MONTH_CHOICES = [
        (1, _('Gennaio')),
        (2, _('Febbraio')),
        (3, _('Marzo')),
        (4, _('Aprile')),
        (5, _('Maggio')),
        (6, _('Giugno')),
        (7, _('Luglio')),
        (8, _('Agosto')),
        (9, _('Settembre')),
        (10, _('Ottobre')),
        (11, _('Novembre')),
        (12, _('Dicembre'))
    ]
    
    dipendente = forms.ModelChoiceField(
        queryset=Dipendente.objects.filter(is_active=True),
        label=_('Dipendente'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    data_inizio = forms.DateField(
        label=_('Data inizio'),
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    data_fine = forms.DateField(
        label=_('Data fine'),
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Imposta valori iniziali: data di inizio = primo giorno del mese corrente
        # data di fine = ultimo giorno del mese corrente
        today = timezone.localdate()
        first_day = today.replace(day=1)
        
        if not self.is_bound:  # Se il form non è stato inviato
            self.fields['data_inizio'].initial = first_day
            
            # Ultimo giorno del mese
            if today.month == 12:
                last_day = today.replace(year=today.year + 1, month=1, day=1) - timezone.timedelta(days=1)
            else:
                last_day = today.replace(month=today.month + 1, day=1) - timezone.timedelta(days=1)
            
            self.fields['data_fine'].initial = last_day
    
    def clean(self):
        cleaned_data = super().clean()
        data_inizio = cleaned_data.get('data_inizio')
        data_fine = cleaned_data.get('data_fine')
        
        if data_inizio and data_fine and data_inizio > data_fine:
            raise forms.ValidationError(_("La data di inizio deve essere precedente alla data di fine."))
        
        return cleaned_data