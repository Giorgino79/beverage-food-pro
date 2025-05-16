from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, ReadOnlyPasswordHashField
from django.utils.translation import gettext_lazy as _
from .models import Dipendente, AllegatoDipendente, Giornata

class DateInput(forms.DateInput):
    """Widget personalizzato per i campi data"""
    input_type = "date"

class TimeInput(forms.TimeInput):
    """Widget personalizzato per i campi ora"""
    input_type = "time"

class DipendenteForm(forms.ModelForm):
    """Base form per i dipendenti con validazione avanzata"""
    
    class Meta:
        model = Dipendente
        fields = [
            'username', 'email', 'first_name', 'last_name', 'livello',
            'indirizzo', 'telefono', 'data_nascita', 'data_assunzione',
            'CF', 'carta_d_identità', 'data_scadenza_ci', 
            'patente_di_guida', 'data_scadenza_patente', 'categorie_patente',
            'posizione_inail', 'posizione_inps',
            'foto_dipendente', 'foto_carta_identità', 'foto_codice_fiscale', 'foto_patente',
            'note'
        ]
        widgets = {
            'data_nascita': DateInput(),
            'data_assunzione': DateInput(),
            'data_scadenza_ci': DateInput(),
            'data_scadenza_patente': DateInput(),
            'note': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_CF(self):
        """Validazione del codice fiscale"""
        cf = self.cleaned_data.get('CF')
        if cf:
            # Rimuove spazi e converte in maiuscolo
            cf = cf.replace(' ', '').upper()
            
            # Verifica lunghezza
            if len(cf) != 16:
                raise forms.ValidationError(_("Il codice fiscale deve essere di 16 caratteri"))
            
            # Verifica pattern (implementazione base)
            import re
            pattern = r'^[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]$'
            if not re.match(pattern, cf):
                raise forms.ValidationError(_("Formato del codice fiscale non valido"))
            
            return cf
        return None

class DipendenteCreationForm(UserCreationForm, DipendenteForm):
    """Form per la creazione di un nuovo dipendente"""
    
    class Meta(DipendenteForm.Meta):
        fields = ['username', 'password1', 'password2'] + DipendenteForm.Meta.fields
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = _("Inserire un nome utente univoco. Max 150 caratteri.")
        self.fields['password1'].help_text = _("La password deve contenere almeno 8 caratteri.")

class DipendenteChangeForm(DipendenteForm):
    """Form per la modifica di un dipendente esistente"""
    
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_("Le password non sono memorizzate in chiaro, quindi non è possibile "
                  "visualizzare la password di questo utente, ma è possibile modificarla "
                  "usando <a href=\"../password/\">questo form</a>.")
    )
    
    class Meta(DipendenteForm.Meta):
        fields = ['password', 'is_active', 'is_staff'] + DipendenteForm.Meta.fields

class AllegatoDipendenteForm(forms.ModelForm):
    """Form per la gestione degli allegati"""
    
    class Meta:
        model = AllegatoDipendente
        fields = ['tipo', 'nome', 'file', 'visibile_al_dipendente', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 2}),
        }
        
    def clean_file(self):
        """Validazione del file caricato"""
        file = self.cleaned_data.get('file')
        if file:
            # Verifica estensione
            ext = file.name.split('.')[-1].lower()
            allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx']
            if ext not in allowed_extensions:
                raise forms.ValidationError(
                    _("Formato file non supportato. Formati consentiti: {0}").format(
                        ', '.join(allowed_extensions)
                    )
                )
            
            # Verifica dimensione (max 5MB)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError(_("Il file non deve superare i 5MB"))
                
        return file

class GiornataFormBase(forms.ModelForm):
    """Form base per la gestione delle giornate lavorative"""
    
    class Meta:
        model = Giornata
        fields = []
        widgets = {
            'ora_inizio_mattina': TimeInput(),
            'ora_fine_mattina': TimeInput(),
            'ora_inizio_pomeriggio': TimeInput(),
            'ora_fine_pomeriggio': TimeInput(),
        }
    
    def clean(self):
        """Validazione degli orari"""
        cleaned_data = super().clean()
        
        inizio_mattina = cleaned_data.get('ora_inizio_mattina')
        fine_mattina = cleaned_data.get('ora_fine_mattina')
        inizio_pomeriggio = cleaned_data.get('ora_inizio_pomeriggio')
        fine_pomeriggio = cleaned_data.get('ora_fine_pomeriggio')
        
        # Se inserito fine mattina, deve esserci anche inizio mattina
        if fine_mattina and not inizio_mattina:
            self.add_error('ora_fine_mattina', _("Inserire anche l'ora di inizio mattina"))
            
        # Se inserito inizio pomeriggio, deve esserci anche fine pomeriggio
        if inizio_pomeriggio and not fine_pomeriggio:
            self.add_error('ora_inizio_pomeriggio', _("Inserire anche l'ora di fine pomeriggio"))
            
        # Validazione dell'ordine degli orari
        if inizio_mattina and fine_mattina and inizio_mattina >= fine_mattina:
            self.add_error('ora_fine_mattina', _("L'ora di fine mattina deve essere successiva all'ora di inizio"))
            
        if inizio_pomeriggio and fine_pomeriggio and inizio_pomeriggio >= fine_pomeriggio:
            self.add_error('ora_fine_pomeriggio', _("L'ora di fine pomeriggio deve essere successiva all'ora di inizio"))
            
        if fine_mattina and inizio_pomeriggio and fine_mattina > inizio_pomeriggio:
            self.add_error('ora_inizio_pomeriggio', _("L'ora di inizio pomeriggio deve essere successiva all'ora di fine mattina"))
        
        return cleaned_data

class InizioGiornataForm(GiornataFormBase):
    """Form per l'inizio della giornata lavorativa"""
    
    class Meta(GiornataFormBase.Meta):
        fields = ['ora_inizio_mattina', 'assenza', 'nota_assenza']

class GiornataForm(GiornataFormBase):
    """Form per l'aggiornamento della giornata lavorativa"""
    
    class Meta(GiornataFormBase.Meta):
        fields = ['ora_fine_mattina', 'ora_inizio_pomeriggio', 'ora_fine_pomeriggio', 
                  'assenza', 'nota_assenza', 'chiudi_giornata']

class MensilitaForm(forms.Form):
    """Form per la generazione del report mensile"""
    dipendente = forms.ModelChoiceField(
        queryset=Dipendente.objects.filter(is_active=True),
        label=_("Dipendente")
    )
    data_inizio = forms.DateField(widget=DateInput(), label=_("Data inizio"))
    data_fine = forms.DateField(widget=DateInput(), label=_("Data fine"))
    
    def clean(self):
        cleaned_data = super().clean()
        data_inizio = cleaned_data.get('data_inizio')
        data_fine = cleaned_data.get('data_fine')
        
        if data_inizio and data_fine and data_inizio > data_fine:
            self.add_error('data_fine', _("La data fine deve essere successiva alla data inizio"))
        
        return cleaned_data