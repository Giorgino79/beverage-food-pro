from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.views.generic.base import TemplateView
from django.utils import timezone
from utils import produci_pdf
from datetime import date, datetime, timedelta
from io import BytesIO

from .models import Dipendente, AllegatoDipendente, Giornata
from .forms import (
    DipendenteCreationForm, DipendenteChangeForm, AllegatoDipendenteForm,
    InizioGiornataForm, GiornataForm, MensilitaForm
)

class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin per verificare che l'utente sia staff"""
    def test_func(self):
        return self.request.user.is_staff

class TotaleLivelloRequiredMixin(UserPassesTestMixin):
    """Mixin per verificare che l'utente abbia livello 'totale'"""
    def test_func(self):
        # Corretto per includere i superuser
        return (self.request.user.livello == Dipendente.Autorizzazioni.totale or 
                self.request.user.is_superuser)

class ContabileLivelloRequiredMixin(UserPassesTestMixin):
    """Mixin per verificare che l'utente abbia livello 'contabile' o superiore"""
    def test_func(self):
        # Modificato per includere i superuser
        return self.request.user.livello in [
            Dipendente.Autorizzazioni.totale,
            Dipendente.Autorizzazioni.contabile
        ] or self.request.user.is_superuser

class DipendenteListView(LoginRequiredMixin, ContabileLivelloRequiredMixin, ListView):
    """Vista per l'elenco dei dipendenti"""
    model = Dipendente
    template_name = 'dipendenti/elencodipendenti.html'
    context_object_name = 'dip'
    
    def get_queryset(self):
        """Personalizza la queryset in base alla ricerca"""
        queryset = super().get_queryset().filter(is_active=True)
        
        # Filtra per termine di ricerca
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                username__icontains=search
            ) | queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                last_name__icontains=search
            ) | queryset.filter(
                email__icontains=search
            )
        
        return queryset

class DipendenteDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Vista per i dettagli di un dipendente"""
    model = Dipendente
    template_name = 'dipendenti/vedidipendente.html'
    context_object_name = 'dipen'
    
    def test_func(self):
        """Verifica che l'utente possa visualizzare il dipendente"""
        # L'utente può vedere se stesso o se ha livello contabile o superiore o se è superuser
        return (self.request.user.pk == self.kwargs.get('pk') or
                self.request.user.livello in [Dipendente.Autorizzazioni.totale, 
                                             Dipendente.Autorizzazioni.contabile] or
                self.request.user.is_superuser)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Aggiungi gli allegati visibili all'utente
        if self.request.user.livello in [Dipendente.Autorizzazioni.totale, Dipendente.Autorizzazioni.contabile] or self.request.user.is_superuser:
            # Admin, superuser e contabili vedono tutti gli allegati
            context['allegati'] = AllegatoDipendente.objects.filter(dipendente=self.object)
        else:
            # Gli altri utenti vedono solo i propri allegati visibili
            context['allegati'] = AllegatoDipendente.objects.filter(
                dipendente=self.object, 
                visibile_al_dipendente=True
            )
        
        # Aggiungi le giornate lavorative
        oggi = date.today()
        context['giornata_oggi'] = Giornata.objects.filter(
            operatore=self.object, 
            data=oggi
        ).first()
        
        # Giornate recenti
        context['giornate_recenti'] = Giornata.objects.filter(
            operatore=self.object
        ).order_by('-data')[:10]
        
        return context

class DipendenteCreateView(LoginRequiredMixin, TotaleLivelloRequiredMixin, CreateView):
    """Vista per la creazione di un nuovo dipendente"""
    model = Dipendente
    form_class = DipendenteCreationForm
    template_name = 'dipendenti/nuovodipendente.html'
    success_url = reverse_lazy('dipendenti:elencodipendenti')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, 
            _('Nuovo dipendente con username {0} creato con successo!').format(form.instance.username)
        )
        return response

class DipendenteUpdateView(LoginRequiredMixin, ContabileLivelloRequiredMixin, UpdateView):
    """Vista per l'aggiornamento di un dipendente esistente"""
    model = Dipendente
    form_class = DipendenteChangeForm
    template_name = 'dipendenti/aggiornadipendente.html'
    
    def get_success_url(self):
        return reverse_lazy('dipendenti:vedidipendente', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, 
            _('Dipendente {0} aggiornato con successo!').format(form.instance.username)
        )
        return response

class AllegatoCreateView(LoginRequiredMixin, ContabileLivelloRequiredMixin, CreateView):
    """Vista per l'aggiunta di un allegato a un dipendente"""
    model = AllegatoDipendente
    form_class = AllegatoDipendenteForm
    template_name = 'dipendenti/nuovo_allegato.html'
    
    def form_valid(self, form):
        form.instance.dipendente_id = self.kwargs.get('dipendente_id')
        response = super().form_valid(form)
        messages.success(
            self.request, 
            _('Allegato "{0}" aggiunto con successo!').format(form.instance.nome)
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy('dipendenti:vedidipendente', kwargs={'pk': self.kwargs.get('dipendente_id')})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dipendente'] = get_object_or_404(Dipendente, pk=self.kwargs.get('dipendente_id'))
        return context

class AllegatoDeleteView(LoginRequiredMixin, ContabileLivelloRequiredMixin, DeleteView):
    """Vista per l'eliminazione di un allegato"""
    model = AllegatoDipendente
    template_name = 'dipendenti/elimina_allegato.html'
    
    def get_success_url(self):
        return reverse_lazy('dipendenti:vedidipendente', kwargs={'pk': self.object.dipendente.pk})
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        nome_allegato = self.object.nome
        self.object.delete()
        messages.success(request, _('Allegato "{0}" eliminato con successo!').format(nome_allegato))
        return HttpResponseRedirect(success_url)

class GiornataCreateView(LoginRequiredMixin, CreateView):
    """Vista per la creazione di una nuova giornata lavorativa"""
    model = Giornata
    form_class = InizioGiornataForm
    template_name = 'dipendenti/iniziogiornata.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Verifica se esiste già una giornata per oggi
        giornata_esistente = Giornata.objects.filter(
            operatore=request.user, 
            data=date.today()
        ).first()
        
        if giornata_esistente:
            return redirect('dipendenti:aggiornagiornata', pk=giornata_esistente.pk)
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.operatore = self.request.user
        form.instance.data = date.today()
        response = super().form_valid(form)
        messages.success(self.request, _('Giornata lavorativa iniziata con successo!'))
        return response
    
    def get_success_url(self):
        return reverse_lazy('dipendenti:profilo', kwargs={'username': self.request.user.username})

class GiornataUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vista per l'aggiornamento di una giornata lavorativa"""
    model = Giornata
    form_class = GiornataForm
    template_name = 'dipendenti/aggiornagiornata.html'
    
    def test_func(self):
        """Verifica che l'utente possa modificare la giornata"""
        giornata = self.get_object()
        # L'utente può modificare la propria giornata non confermata o se è staff o superuser
        if self.request.user.is_staff or self.request.user.is_superuser:
            return True
        return self.request.user == giornata.operatore and not giornata.confermata
    
    def form_valid(self, form):
        # Se la giornata viene chiusa, aggiorna i dati di chiusura
        if form.cleaned_data.get('chiudi_giornata'):
            form.instance.confermata = True
            form.instance.confermata_da = self.request.user
        
        response = super().form_valid(form)
        messages.success(self.request, _('Giornata lavorativa aggiornata con successo!'))
        return response
    
    def get_success_url(self):
        return reverse_lazy('dipendenti:profilo', kwargs={'username': self.object.operatore.username})

class ReportMensileView(LoginRequiredMixin, TotaleLivelloRequiredMixin, FormView):
    """Vista per generare il report mensile delle ore lavorate"""
    template_name = 'dipendenti/stampamesedipendente.html'
    form_class = MensilitaForm
    
    def form_valid(self, form):
        dipendente_id = form.cleaned_data['dipendente'].id
        data_inizio = form.cleaned_data['data_inizio']
        data_fine = form.cleaned_data['data_fine']
        
        # Ottieni il dipendente
        dipendente = get_object_or_404(Dipendente, pk=dipendente_id)
        
        # Ottieni le giornate nel periodo specificato
        giornate = Giornata.objects.filter(
            operatore=dipendente,
            data__gte=data_inizio,
            data__lte=data_fine
        ).order_by('data')
        
        # Calcola le ore totali
        ore_totali = timedelta()
        for giornata in giornate:
            ore_giornata = giornata.daily_hours()
            if ore_giornata:
                ore_totali += ore_giornata
        
        # Prepara il contesto per il template
        context = {
            'dipendente': dipendente,
            'giornate': giornate,
            'data_inizio': data_inizio,
            'data_fine': data_fine,
            'ore_totali': ore_totali,
        }
        
        # Genera il PDF
        template_path = 'dipendenti/oremese.html'
        
        # Utilizza la funzione produci_pdf da utils.py
        try:
            
            pdf = produci_pdf(
                template_path, 
                context, 
                filename=f"Ore_{dipendente.username}_{data_inizio}_{data_fine}.pdf"
            )
            
            # Verifica se il PDF è stato generato correttamente
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                response['Content-Disposition'] = f'filename=Ore_{dipendente.username}.pdf'
                return response
        except ImportError:
            messages.error(self.request, _("Modulo produci_pdf non trovato"))
        except Exception as e:
            messages.error(self.request, _("Si è verificato un errore nella generazione del PDF: {0}").format(str(e)))
        
        # In caso di errore
        return self.form_invalid(form)

def entra(request):
    """Vista per l'accesso al sistema"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            nome = user.username
            messages.success(request, _('Buongiorno {0}!').format(nome))
            return redirect('home:index')  # Cambia in base alla tua configurazione
        else:
            messages.error(request, _('Le credenziali inserite non sono valide. Riprova.'))
    return render(request, 'dipendenti/login.html')

def esci(request):
    """Vista per il logout dal sistema"""
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.success(request, f'Arrivederci {username}!')
    return redirect('home:landing_page')

@login_required
def profilo(request, username):
    """Vista per visualizzare il profilo utente"""
    user = get_object_or_404(Dipendente, username=username)
    oggi = date.today()
    
    # Verifica che l'utente possa vedere il profilo richiesto
    if user != request.user and not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, _("Non hai i permessi per visualizzare questo profilo"))
        return redirect('dipendenti:profilo', username=request.user.username)
    
    # Controlla se esiste una giornata per oggi
    giornata_oggi = Giornata.objects.filter(operatore=user, data=oggi).first()
    
    # Recupera le giornate recenti
    giornate_recenti = Giornata.objects.filter(operatore=user).order_by('-data')[:10]
    
    # Calcola il totale delle ore per la settimana e il mese corrente
    inizio_settimana = oggi - timedelta(days=oggi.weekday())
    inizio_mese = oggi.replace(day=1)
    
    ore_settimanali = timedelta()
    giornate_settimana = Giornata.objects.filter(operatore=user, data__gte=inizio_settimana)
    for giornata in giornate_settimana:
        ore = giornata.daily_hours()
        if ore:
            ore_settimanali += ore
    
    ore_mensili = timedelta()
    giornate_mese = Giornata.objects.filter(operatore=user, data__gte=inizio_mese)
    for giornata in giornate_mese:
        ore = giornata.daily_hours()
        if ore:
            ore_mensili += ore
            
    context = {
        'user': user,
        'giornata_oggi': giornata_oggi,
        'giornate_recenti': giornate_recenti,
        'ore_settimanali': ore_settimanali,
        'ore_mensili': ore_mensili,
        'oggi': oggi,
    }
    
    return render(request, "dipendenti/profilo.html", context)