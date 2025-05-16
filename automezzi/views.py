# automezzi/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
)
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Count, Sum, Avg
from django.http import JsonResponse, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta
from decimal import Decimal
from django.core.paginator import Paginator
from django.db import transaction

from .models import (
    TipoCarburante, Automezzo, DocumentoAutomezzo, 
    Manutenzione, RifornimentoCarburante, EventoAutomezzo, StatisticheAutomezzo
)
from .forms import (
    TipoCarburanteForm, AutomezzoForm, DocumentoAutomezzoForm,
    ManutenzioneForm, RifornimentoCarburanteForm, EventoAutomezzoForm,
    AutomezzoSearchForm, FiltroScadenzeForm
)


# Mixins personalizzati
class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin per verificare che l'utente sia staff"""
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class AutomezziAccessMixin(UserPassesTestMixin):
    """Mixin per controllare l'accesso agli automezzi"""
    def test_func(self):
        # Staff può vedere tutto
        if self.request.user.is_staff or self.request.user.is_superuser:
            return True
        
        # Se l'oggetto è un automezzo, controlla se è assegnato all'utente
        obj = self.get_object()
        if hasattr(obj, 'assegnato_a'):
            return obj.assegnato_a == self.request.user
        
        # Per oggetti collegati all'automezzo (documenti, manutenzioni, ecc.)
        if hasattr(obj, 'automezzo'):
            return obj.automezzo.assegnato_a == self.request.user
        
        return False


# ===================== DASHBOARD E OVERVIEW =====================
@login_required
def dashboard_automezzi(request):
    """Dashboard principale dell'app automezzi"""
    
    # Statistiche generali
    stats = {
        'totale_automezzi': Automezzo.objects.filter(attivo=True).count(),
        'automezzi_disponibili': Automezzo.objects.filter(attivo=True, disponibile=True).count(),
        'automezzi_assegnati': Automezzo.objects.filter(attivo=True, assegnato_a__isnull=False).count(),
    }
    
    # Scadenze prossime (prossimi 30 giorni)
    data_limite = date.today() + timedelta(days=30)
    
    # Documenti in scadenza
    documenti_scadenza = DocumentoAutomezzo.objects.filter(
        data_scadenza__gte=date.today(),
        data_scadenza__lte=data_limite
    ).select_related('automezzo').order_by('data_scadenza')[:5]
    
    # Manutenzioni in programma
    manutenzioni_programmate = Manutenzione.objects.filter(
        completata=False,
        data_prevista__lte=data_limite
    ).select_related('automezzo').order_by('data_prevista')[:5]
    
    # Ultimi eventi
    ultimi_eventi = EventoAutomezzo.objects.select_related('automezzo').order_by('-data_evento')[:5]
    
    # Solo per staff: statistiche sui tipi di carburante
    if request.user.is_staff:
        tipi_carburante_stats = TipoCarburante.objects.annotate(
            automezzi_count=Count('automezzo')
        ).order_by('-automezzi_count')
    else:
        tipi_carburante_stats = None
    
    context = {
        'stats': stats,
        'documenti_scadenza': documenti_scadenza,
        'manutenzioni_programmate': manutenzioni_programmate,
        'ultimi_eventi': ultimi_eventi,
        'tipi_carburante_stats': tipi_carburante_stats,
        'giorni_scadenza': 30,
    }
    
    return render(request, 'automezzi/dashboard.html', context)


@login_required
def scadenze_view(request):
    """Vista per tutte le scadenze"""
    form = FiltroScadenzeForm(request.GET or None)
    
    giorni = int(request.GET.get('giorni', 30))
    solo_non_scaduti = request.GET.get('solo_non_scaduti', True)
    
    data_limite = date.today() + timedelta(days=giorni)
    
    # Query base per documenti
    documenti_qs = DocumentoAutomezzo.objects.select_related('automezzo')
    if solo_non_scaduti:
        documenti_qs = documenti_qs.filter(data_scadenza__gte=date.today())
    documenti_qs = documenti_qs.filter(data_scadenza__lte=data_limite)
    
    # Query base per manutenzioni
    manutenzioni_qs = Manutenzione.objects.filter(completata=False).select_related('automezzo')
    if solo_non_scaduti:
        manutenzioni_qs = manutenzioni_qs.filter(data_prevista__gte=date.today())
    manutenzioni_qs = manutenzioni_qs.filter(data_prevista__lte=data_limite)
    
    # Se non è staff, filtra solo gli automezzi assegnati
    if not request.user.is_staff and not request.user.is_superuser:
        documenti_qs = documenti_qs.filter(automezzo__assegnato_a=request.user)
        manutenzioni_qs = manutenzioni_qs.filter(automezzo__assegnato_a=request.user)
    
    context = {
        'form': form,
        'documenti': documenti_qs.order_by('data_scadenza'),
        'manutenzioni': manutenzioni_qs.order_by('data_prevista'),
        'giorni': giorni,
        'solo_non_scaduti': solo_non_scaduti,
    }
    
    return render(request, 'automezzi/scadenze.html', context)


# ===================== TIPO CARBURANTE =====================
class TipoCarburanteListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """Lista dei tipi di carburante"""
    model = TipoCarburante
    template_name = 'automezzi/tipo_carburante/lista.html'
    context_object_name = 'tipi_carburante'
    paginate_by = 20
    
    def get_queryset(self):
        return TipoCarburante.objects.annotate(
            automezzi_count=Count('automezzo', filter=Q(automezzo__attivo=True))
        ).order_by('nome')


class TipoCarburanteCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """Creazione nuovo tipo di carburante"""
    model = TipoCarburante
    form_class = TipoCarburanteForm
    template_name = 'automezzi/tipo_carburante/form.html'
    success_url = reverse_lazy('automezzi:tipi_carburante')
    
    def form_valid(self, form):
        messages.success(self.request, f'Tipo carburante "{form.instance.nome}" creato con successo!')
        return super().form_valid(form)


class TipoCarburanteUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    """Modifica tipo di carburante"""
    model = TipoCarburante
    form_class = TipoCarburanteForm
    template_name = 'automezzi/tipo_carburante/form.html'
    success_url = reverse_lazy('automezzi:tipi_carburante')
    
    def form_valid(self, form):
        messages.success(self.request, f'Tipo carburante "{form.instance.nome}" aggiornato con successo!')
        return super().form_valid(form)


class TipoCarburanteDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    """Eliminazione tipo di carburante"""
    model = TipoCarburante
    template_name = 'automezzi/tipo_carburante/elimina.html'
    success_url = reverse_lazy('automezzi:tipi_carburante')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nome = self.object.nome
        
        # Controlla se ci sono automezzi che usano questo carburante
        if self.object.automezzo_set.exists():
            messages.error(
                request, 
                f'Impossibile eliminare "{nome}": esistono automezzi che utilizzano questo carburante.'
            )
            return HttpResponseRedirect(self.success_url)
        
        self.object.delete()
        messages.success(request, f'Tipo carburante "{nome}" eliminato con successo!')
        return HttpResponseRedirect(self.success_url)


# ===================== AUTOMEZZI =====================
class AutomezzoListView(LoginRequiredMixin, ListView):
    """Lista degli automezzi con ricerca e filtri"""
    model = Automezzo
    template_name = 'automezzi/automezzo/lista.html'
    context_object_name = 'automezzi'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Automezzo.objects.select_related('tipo_carburante', 'assegnato_a')
        
        # Se non è staff, mostra solo automezzi assegnati all'utente
        if not self.request.user.is_staff and not self.request.user.is_superuser:
            queryset = queryset.filter(assegnato_a=self.request.user)
        
        # Gestione ricerca
        form = AutomezzoSearchForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data['q']
            if q:
                queryset = queryset.filter(
                    Q(targa__icontains=q) |
                    Q(marca__icontains=q) |
                    Q(modello__icontains=q)
                )
            
            tipo_carburante = form.cleaned_data['tipo_carburante']
            if tipo_carburante:
                queryset = queryset.filter(tipo_carburante=tipo_carburante)
            
            assegnato_a = form.cleaned_data['assegnato_a']
            if assegnato_a:
                queryset = queryset.filter(assegnato_a=assegnato_a)
            
            solo_attivi = form.cleaned_data['solo_attivi']
            if solo_attivi:
                queryset = queryset.filter(attivo=True)
        
        return queryset.order_by('targa')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = AutomezzoSearchForm(self.request.GET)
        return context


class AutomezzoDetailView(LoginRequiredMixin, AutomezziAccessMixin, DetailView):
    """Dettaglio automezzo con navigazione tra sezioni"""
    model = Automezzo
    template_name = 'automezzi/automezzo/dettaglio.html'
    context_object_name = 'automezzo'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        automezzo = self.object
        
        # Sezione da visualizzare (default: documenti)
        sezione = self.request.GET.get('sezione', 'documenti')
        context['sezione_attiva'] = sezione
        
        # Documenti
        context['documenti'] = automezzo.documenti.order_by('-data_scadenza')
        
        # Manutenzioni
        context['manutenzioni'] = automezzo.manutenzioni.select_related('responsabile').order_by('-data_prevista')
        context['manutenzioni_completate'] = context['manutenzioni'].filter(completata=True)[:5]
        context['manutenzioni_programmate'] = context['manutenzioni'].filter(completata=False)
        
        # Rifornimenti con calcolo consumi
        rifornimenti = automezzo.rifornimenti.select_related('effettuato_da').order_by('-data_rifornimento')
        context['rifornimenti'] = rifornimenti[:10]  # Ultimi 10
        
        # Calcolo statistiche carburante
        if rifornimenti.exists():
            context['consumo_medio'] = self._calcola_consumo_medio(rifornimenti)
            context['costo_medio_litro'] = rifornimenti.aggregate(
                media=Avg('costo_per_litro')
            )['media']
        
        # Eventi
        context['eventi'] = automezzo.eventi.select_related('dipendente_coinvolto').order_by('-data_evento')
        
        # Prossime scadenze
        context['prossime_scadenze'] = automezzo.prossime_scadenze(30)
        
        return context
    
    def _calcola_consumo_medio(self, rifornimenti):
        """Calcola il consumo medio dell'automezzo"""
        consumi = []
        for rif in rifornimenti:
            consumo = rif.consumo_per_100km
            if consumo and consumo > 0:
                consumi.append(consumo)
        
        if consumi:
            return sum(consumi) / len(consumi)
        return None


class AutomezzoCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """Creazione nuovo automezzo"""
    model = Automezzo
    form_class = AutomezzoForm
    template_name = 'automezzi/automezzo/form.html'
    
    def form_valid(self, form):
        messages.success(self.request, f'Automezzo "{form.instance.targa}" creato con successo!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('automezzi:dettaglio', kwargs={'pk': self.object.pk})


class AutomezzoUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    """Modifica automezzo"""
    model = Automezzo
    form_class = AutomezzoForm
    template_name = 'automezzi/automezzo/form.html'
    
    def form_valid(self, form):
        messages.success(self.request, f'Automezzo "{form.instance.targa}" aggiornato con successo!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('automezzi:dettaglio', kwargs={'pk': self.object.pk})


class AutomezzoDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    """Eliminazione automezzo"""
    model = Automezzo
    template_name = 'automezzi/automezzo/elimina.html'
    success_url = reverse_lazy('automezzi:lista')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        targa = self.object.targa
        
        # Soft delete: imposta come non attivo invece di eliminare
        self.object.attivo = False
        self.object.disponibile = False
        self.object.save()
        
        messages.success(request, f'Automezzo "{targa}" disattivato con successo!')
        return HttpResponseRedirect(self.success_url)


# ===================== DOCUMENTI =====================
class DocumentoCreateView(LoginRequiredMixin, CreateView):
    """Creazione nuovo documento per automezzo"""
    model = DocumentoAutomezzo
    form_class = DocumentoAutomezzoForm
    template_name = 'automezzi/documento/form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.automezzo = get_object_or_404(Automezzo, pk=kwargs['automezzo_pk'])
        
        # Controllo permessi
        if not (request.user.is_staff or request.user.is_superuser or 
                self.automezzo.assegnato_a == request.user):
            messages.error(request, "Non hai i permessi per aggiungere documenti a questo automezzo.")
            return redirect('automezzi:dettaglio', pk=self.automezzo.pk)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['automezzo'] = self.automezzo
        return kwargs
    
    def form_valid(self, form):
        form.instance.automezzo = self.automezzo
        messages.success(
            self.request, 
            f'Documento "{form.instance.get_tipo_display()}" aggiunto con successo!'
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('automezzi:dettaglio', kwargs={'pk': self.automezzo.pk}) + '?sezione=documenti'


class DocumentoUpdateView(LoginRequiredMixin, AutomezziAccessMixin, UpdateView):
    """Modifica documento automezzo"""
    model = DocumentoAutomezzo
    form_class = DocumentoAutomezzoForm
    template_name = 'automezzi/documento/form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['automezzo'] = self.object.automezzo
        return kwargs
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            f'Documento "{form.instance.get_tipo_display()}" aggiornato con successo!'
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('automezzi:dettaglio', kwargs={'pk': self.object.automezzo.pk}) + '?sezione=documenti'


class DocumentoDeleteView(LoginRequiredMixin, AutomezziAccessMixin, DeleteView):
    """Eliminazione documento"""
    model = DocumentoAutomezzo
    template_name = 'automezzi/documento/elimina.html'
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        automezzo_pk = self.object.automezzo.pk
        tipo = self.object.get_tipo_display()
        
        self.object.delete()
        messages.success(request, f'Documento "{tipo}" eliminato con successo!')
        return HttpResponseRedirect(
            reverse('automezzi:dettaglio', kwargs={'pk': automezzo_pk}) + '?sezione=documenti'
        )


# ===================== MANUTENZIONI =====================
class ManutenzioneCreateView(LoginRequiredMixin, CreateView):
    """Creazione nuova manutenzione"""
    model = Manutenzione
    form_class = ManutenzioneForm
    template_name = 'automezzi/manutenzione/form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.automezzo = get_object_or_404(Automezzo, pk=kwargs['automezzo_pk'])
        
        # Controllo permessi
        if not (request.user.is_staff or request.user.is_superuser or 
                self.automezzo.assegnato_a == request.user):
            messages.error(request, "Non hai i permessi per aggiungere manutenzioni a questo automezzo.")
            return redirect('automezzi:dettaglio', pk=self.automezzo.pk)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['automezzo'] = self.automezzo
        return kwargs
    
    def form_valid(self, form):
        form.instance.automezzo = self.automezzo
        
        # Se non specificato e l'utente non è staff, imposta come responsabile l'utente corrente
        if not form.instance.responsabile and not self.request.user.is_staff:
            form.instance.responsabile = self.request.user
        
        messages.success(
            self.request, 
            f'Manutenzione "{form.instance.get_tipo_display()}" programmata con successo!'
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('automezzi:dettaglio', kwargs={'pk': self.automezzo.pk}) + '?sezione=manutenzioni'


class ManutenzioneUpdateView(LoginRequiredMixin, AutomezziAccessMixin, UpdateView):
    """Modifica manutenzione"""
    model = Manutenzione
    form_class = ManutenzioneForm
    template_name = 'automezzi/manutenzione/form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['automezzo'] = self.object.automezzo
        return kwargs
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            f'Manutenzione "{form.instance.get_tipo_display()}" aggiornata con successo!'
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('automezzi:dettaglio', kwargs={'pk': self.object.automezzo.pk}) + '?sezione=manutenzioni'


@login_required
def manutenzione_completa(request, pk):
    """Marca una manutenzione come completata"""
    manutenzione = get_object_or_404(Manutenzione, pk=pk)
    
    # Controllo permessi
    if not (request.user.is_staff or request.user.is_superuser or 
            manutenzione.automezzo.assegnato_a == request.user or
            manutenzione.responsabile == request.user):
        messages.error(request, "Non hai i permessi per completare questa manutenzione.")
        return redirect('automezzi:dettaglio', pk=manutenzione.automezzo.pk)
    
    if not manutenzione.completata:
        manutenzione.completata = True
        manutenzione.data_effettuata = date.today()
        manutenzione.save()
        
        messages.success(
            request, 
            f'Manutenzione "{manutenzione.get_tipo_display()}" marcata come completata!'
        )
    else:
        messages.info(request, "La manutenzione era già stata completata.")
    
    return redirect('automezzi:dettaglio', pk=manutenzione.automezzo.pk, sezione='manutenzioni')


# ===================== RIFORNIMENTI =====================
class RifornimentoCreateView(LoginRequiredMixin, CreateView):
    """Registrazione nuovo rifornimento"""
    model = RifornimentoCarburante
    form_class = RifornimentoCarburanteForm
    template_name = 'automezzi/rifornimento/form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.automezzo = get_object_or_404(Automezzo, pk=kwargs['automezzo_pk'])
        
        # Controllo permessi
        if not (request.user.is_staff or request.user.is_superuser or 
                self.automezzo.assegnato_a == request.user):
            messages.error(request, "Non hai i permessi per registrare rifornimenti per questo automezzo.")
            return redirect('automezzi:dettaglio', pk=self.automezzo.pk)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['automezzo'] = self.automezzo
        return kwargs
    
    def form_valid(self, form):
        form.instance.automezzo = self.automezzo
        
        # Se non specificato, imposta l'utente corrente come chi ha effettuato il rifornimento
        if not form.instance.effettuato_da:
            form.instance.effettuato_da = self.request.user
        
        messages.success(self.request, 'Rifornimento registrato con successo!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('automezzi:dettaglio', kwargs={'pk': self.automezzo.pk}) + '?sezione=rifornimenti'


class RifornimentoUpdateView(LoginRequiredMixin, AutomezziAccessMixin, UpdateView):
    """Modifica rifornimento"""
    model = RifornimentoCarburante
    form_class = RifornimentoCarburanteForm
    template_name = 'automezzi/rifornimento/form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['automezzo'] = self.object.automezzo
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Rifornimento aggiornato con successo!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('automezzi:dettaglio', kwargs={'pk': self.object.automezzo.pk}) + '?sezione=rifornimenti'


# ===================== EVENTI =====================
class EventoCreateView(LoginRequiredMixin, CreateView):
    """Registrazione nuovo evento"""
    model = EventoAutomezzo
    form_class = EventoAutomezzoForm
    template_name = 'automezzi/evento/form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.automezzo = get_object_or_404(Automezzo, pk=kwargs['automezzo_pk'])
        
        # Controllo permessi
        if not (request.user.is_staff or request.user.is_superuser or 
                self.automezzo.assegnato_a == request.user):
            messages.error(request, "Non hai i permessi per registrare eventi per questo automezzo.")
            return redirect('automezzi:dettaglio', pk=self.automezzo.pk)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['automezzo'] = self.automezzo
        return kwargs
    
    def form_valid(self, form):
        form.instance.automezzo = self.automezzo
        
        # Se non specificato, imposta l'utente corrente come dipendente coinvolto
        if not form.instance.dipendente_coinvolto:
            form.instance.dipendente_coinvolto = self.request.user
        
        messages.success(
            self.request, 
            f'Evento "{form.instance.get_tipo_display()}" registrato con successo!'
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('automezzi:dettaglio', kwargs={'pk': self.automezzo.pk}) + '?sezione=eventi'


class EventoUpdateView(LoginRequiredMixin, AutomezziAccessMixin, UpdateView):
    """Modifica evento"""
    model = EventoAutomezzo
    form_class = EventoAutomezzoForm
    template_name = 'automezzi/evento/form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['automezzo'] = self.object.automezzo
        return kwargs
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            f'Evento "{form.instance.get_tipo_display()}" aggiornato con successo!'
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('automezzi:dettaglio', kwargs={'pk': self.object.automezzo.pk}) + '?sezione=eventi'


@login_required
def evento_risolvi(request, pk):
    """Marca un evento come risolto"""
    evento = get_object_or_404(EventoAutomezzo, pk=pk)
    
    # Controllo permessi
    if not (request.user.is_staff or request.user.is_superuser or 
            evento.automezzo.assegnato_a == request.user or
            evento.dipendente_coinvolto == request.user):
        messages.error(request, "Non hai i permessi per risolvere questo evento.")
        return redirect('automezzi:dettaglio', pk=evento.automezzo.pk)
    
    if not evento.risolto:
        evento.risolto = True
        evento.save()
        
        messages.success(
            request, 
            f'Evento "{evento.get_tipo_display()}" marcato come risolto!'
        )
    else:
        messages.info(request, "L'evento era già stato risolto.")
    
    return redirect('automezzi:dettaglio', pk=evento.automezzo.pk, sezione='eventi')


# ===================== API E UTILITY =====================
@login_required
def api_automezzi_search(request):
    """API per ricerca automezzi (utilizzata in altri moduli)"""
    q = request.GET.get('q', '')
    
    queryset = Automezzo.objects.filter(attivo=True)
    
    # Se non è staff, filtra solo automezzi assegnati
    if not request.user.is_staff and not request.user.is_superuser:
        queryset = queryset.filter(assegnato_a=request.user)
    
    if q:
        queryset = queryset.filter(
            Q(targa__icontains=q) |
            Q(marca__icontains=q) |
            Q(modello__icontains=q)
        )
    
    results = []
    for automezzo in queryset[:10]:  # Limita a 10 risultati
        results.append({
            'id': automezzo.id,
            'text': f"{automezzo.targa} - {automezzo.marca} {automezzo.modello}",
            'data': {
                'targa': automezzo.targa,
                'marca': automezzo.marca,
                'modello': automezzo.modello,
                'carburante': automezzo.tipo_carburante.nome,
                'assegnato_a': automezzo.assegnato_a.get_full_name() if automezzo.assegnato_a else None
            }
        })
    
    return JsonResponse({'results': results})


@login_required
def toggle_disponibilita(request, pk):
    """Toggle della disponibilità di un automezzo"""
    automezzo = get_object_or_404(Automezzo, pk=pk)
    
    # Solo staff può modificare la disponibilità
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Non hai i permessi per modificare la disponibilità di questo automezzo.")
        return redirect('automezzi:dettaglio', pk=pk)
    
    automezzo.disponibile = not automezzo.disponibile
    automezzo.save()
    
    status = "disponibile" if automezzo.disponibile else "non disponibile"
    messages.success(
        request, 
        f'Automezzo {automezzo.targa} ora è {status}.'
    )
    
    return redirect('automezzi:dettaglio', pk=pk)


@login_required
def aggiorna_statistiche(request, pk):
    """Aggiorna le statistiche di un automezzo"""
    automezzo = get_object_or_404(Automezzo, pk=pk)
    
    # Solo staff può aggiornare le statistiche
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Non hai i permessi per aggiornare le statistiche.")
        return redirect('automezzi:dettaglio', pk=pk)
    
    # Crea o ottieni le statistiche
    statistiche, created = StatisticheAutomezzo.objects.get_or_create(automezzo=automezzo)
    
    # Aggiorna le statistiche
    statistiche.aggiorna_statistiche()
    
    messages.success(request, f'Statistiche per {automezzo.targa} aggiornate con successo!')
    return redirect('automezzi:dettaglio', pk=pk)


@login_required
def report_consumi(request, pk):
    """Genera report dei consumi per un automezzo"""
    automezzo = get_object_or_404(Automezzo, pk=pk)
    
    # Controllo permessi
    if not (request.user.is_staff or request.user.is_superuser or 
            automezzo.assegnato_a == request.user):
        messages.error(request, "Non hai i permessi per visualizzare questo report.")
        return redirect('automezzi:dettaglio', pk=pk)
    
    # Get date range from request
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    # Default to last 6 months if no dates provided
    if not from_date:
        from_date = (date.today() - timedelta(days=180)).strftime('%Y-%m-%d')
    if not to_date:
        to_date = date.today().strftime('%Y-%m-%d')
    
    # Convert strings to date objects
    from django.utils.dateparse import parse_date
    from_date = parse_date(from_date)
    to_date = parse_date(to_date)
    
    # Get rifornimenti in date range
    rifornimenti = automezzo.rifornimenti.filter(
        data_rifornimento__gte=from_date,
        data_rifornimento__lte=to_date
    ).order_by('data_rifornimento')
    
    # Calculate statistics
    stats = {
        'automezzo': automezzo,
        'from_date': from_date,
        'to_date': to_date,
        'num_rifornimenti': rifornimenti.count(),
        'litri_totali': rifornimenti.aggregate(Sum('litri'))['litri__sum'] or 0,
        'costo_totale': rifornimenti.aggregate(Sum('costo_totale'))['costo_totale__sum'] or 0,
        'km_percorsi': 0,
        'consumo_medio': 0,
        'costo_medio_litro': 0,
    }
    
    if rifornimenti.exists():
        primo_rif = rifornimenti.first()
        ultimo_rif = rifornimenti.last()
        stats['km_percorsi'] = ultimo_rif.chilometri - primo_rif.chilometri_precedente
        
        if stats['km_percorsi'] > 0:
            stats['consumo_medio'] = (stats['litri_totali'] / stats['km_percorsi']) * 100
        
        stats['costo_medio_litro'] = rifornimenti.aggregate(
            Avg('costo_per_litro')
        )['costo_per_litro__avg'] or 0
    
    # Prepare data for charts (monthly breakdown)
    monthly_data = {}
    for rif in rifornimenti:
        month_key = rif.data_rifornimento.strftime('%Y-%m')
        if month_key not in monthly_data:
            monthly_data[month_key] = {
                'litri': 0,
                'costo': 0,
                'count': 0
            }
        monthly_data[month_key]['litri'] += rif.litri
        monthly_data[month_key]['costo'] += rif.costo_totale
        monthly_data[month_key]['count'] += 1
    
    context = {
        'stats': stats,
        'rifornimenti': rifornimenti,
        'monthly_data': monthly_data,
    }
    
    return render(request, 'automezzi/report_consumi.html', context)


# ===================== VIEWS PER LISTE GENERALI =====================
class ManutenzioniListView(LoginRequiredMixin, ListView):
    """Lista di tutte le manutenzioni"""
    model = Manutenzione
    template_name = 'automezzi/manutenzione/lista.html'
    context_object_name = 'manutenzioni'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Manutenzione.objects.select_related('automezzo', 'responsabile')
        
        # Se non è staff, filtra solo manutenzioni degli automezzi assegnati
        if not self.request.user.is_staff and not self.request.user.is_superuser:
            queryset = queryset.filter(
                Q(automezzo__assegnato_a=self.request.user) |
                Q(responsabile=self.request.user)
            )
        
        # Filtri
        status = self.request.GET.get('status')
        if status == 'programmate':
            queryset = queryset.filter(completata=False)
        elif status == 'completate':
            queryset = queryset.filter(completata=True)
        
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        return queryset.order_by('-data_prevista')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Manutenzione.TIPO_MANUTENZIONE_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        context['current_tipo'] = self.request.GET.get('tipo', '')
        return context


class EventiListView(LoginRequiredMixin, ListView):
    """Lista di tutti gli eventi"""
    model = EventoAutomezzo
    template_name = 'automezzi/evento/lista.html'
    context_object_name = 'eventi'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = EventoAutomezzo.objects.select_related('automezzo', 'dipendente_coinvolto')
        
        # Se non è staff, filtra solo eventi degli automezzi assegnati
        if not self.request.user.is_staff and not self.request.user.is_superuser:
            queryset = queryset.filter(
                Q(automezzo__assegnato_a=self.request.user) |
                Q(dipendente_coinvolto=self.request.user)
            )
        
        # Filtri
        status = self.request.GET.get('status')
        if status == 'aperti':
            queryset = queryset.filter(risolto=False)
        elif status == 'risolti':
            queryset = queryset.filter(risolto=True)
        
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        return queryset.order_by('-data_evento')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipo_choices'] = EventoAutomezzo.TIPO_EVENTO_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        context['current_tipo'] = self.request.GET.get('tipo', '')
        return context


# ===================== EXPORT E REPORTS =====================
@login_required
def export_automezzi_csv(request):
    """Export degli automezzi in formato CSV"""
    import csv
    from django.http import HttpResponse
    
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Non hai i permessi per esportare i dati.")
        return redirect('automezzi:lista')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="automezzi.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Targa', 'Marca', 'Modello', 'Anno', 'Tipo Carburante',
        'Km Iniziali', 'Km Attuali', 'Km Totali', 'Assegnato A',
        'Attivo', 'Disponibile'
    ])
    
    for automezzo in Automezzo.objects.select_related('tipo_carburante', 'assegnato_a'):
        writer.writerow([
            automezzo.targa,
            automezzo.marca,
            automezzo.modello,
            automezzo.anno_immatricolazione,
            automezzo.tipo_carburante.nome,
            automezzo.chilometri_iniziali,
            automezzo.chilometri_attuali,
            automezzo.chilometri_totali,
            automezzo.assegnato_a.get_full_name() if automezzo.assegnato_a else '',
            'Sì' if automezzo.attivo else 'No',
            'Sì' if automezzo.disponibile else 'No',
        ])
    
    return response


# ===================== GESTIONE BULK =====================
@login_required
def bulk_aggiorna_disponibilita(request):
    """Aggiorna la disponibilità di più automezzi"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Non hai i permessi per questa operazione.")
        return redirect('automezzi:lista')
    
    if request.method == 'POST':
        automezzo_ids = request.POST.getlist('automezzo_ids')
        azione = request.POST.get('azione')
        
        if automezzo_ids and azione in ['disponibile', 'non_disponibile']:
            automezzi = Automezzo.objects.filter(id__in=automezzo_ids)
            disponibile = azione == 'disponibile'
            
            updated = automezzi.update(disponibile=disponibile)
            status = "disponibili" if disponibile else "non disponibili"
            
            messages.success(
                request, 
                f'{updated} automezzi marcati come {status}.'
            )
        else:
            messages.error(request, "Selezione o azione non valida.")
    
    return redirect('automezzi:lista')


# ===================== GESTIONE ERRORI =====================
def handler404(request, exception):
    """Handler personalizzato per 404"""
    return render(request, 'automezzi/errors/404.html', status=404)


def handler500(request):
    """Handler personalizzato per 500"""
    return render(request, 'automezzi/errors/500.html', status=500)