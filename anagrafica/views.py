# anagrafica/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q, Count
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth.models import Group
from django.utils.translation import gettext as _
import csv
import json

from .models import Rappresentante, Cliente, Fornitore
from .forms import RappresentanteForm, ClienteForm, FornitoreForm, AnagraficaSearchForm
from dipendenti.models import Dipendente


class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin per verificare che l'utente sia staff"""
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class RappresentanteAccessMixin(UserPassesTestMixin):
    """Mixin per controllare accesso rappresentanti ai propri clienti"""
    def test_func(self):
        user = self.request.user
        # Staff e superuser possono accedere a tutto
        if user.is_staff or user.is_superuser:
            return True
        
        # Rappresentanti possono accedere solo ai propri clienti
        if hasattr(user, 'rappresentante'):
            # Se è una vista di dettaglio/modifica cliente, verifica ownership
            if hasattr(self, 'get_object'):
                obj = self.get_object()
                if isinstance(obj, Cliente):
                    return obj.rappresentante == user.rappresentante
            return True
        
        return False


# ================== DASHBOARD ==================

@login_required
def dashboard_anagrafica(request):
    """Dashboard principale dell'anagrafica"""
    context = {
        'totale_rappresentanti': Rappresentante.objects.filter(attivo=True).count(),
        'totale_clienti': Cliente.objects.filter(attivo=True).count(),
        'totale_fornitori': Fornitore.objects.filter(attivo=True).count(),
        'rappresentanti_senza_clienti': Rappresentante.objects.filter(
            attivo=True, clienti__isnull=True
        ).count(),
        'page_title': 'Dashboard Anagrafica',
    }
    return render(request, 'anagrafica/dashboard.html', context)


# ================== RAPPRESENTANTI ==================

class RappresentanteListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """Lista rappresentanti"""
    model = Rappresentante
    template_name = 'anagrafica/rappresentanti/elenco.html'
    context_object_name = 'rappresentanti'
    paginate_by = 20

    def get_queryset(self):
        return Rappresentante.objects.select_related('dipendente').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Elenco Rappresentanti'
        return context


class RappresentanteDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    """Dettaglio rappresentante"""
    model = Rappresentante
    template_name = 'anagrafica/rappresentanti/dettaglio.html'
    context_object_name = 'rappresentante'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Rappresentante: {self.object}'
        # Aggiungi clienti del rappresentante
        context['clienti'] = self.object.clienti.filter(attivo=True)[:10]
        return context


class RappresentanteCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """Creazione rappresentante"""
    model = Rappresentante
    form_class = RappresentanteForm
    template_name = 'anagrafica/rappresentanti/nuovo.html'
    success_url = reverse_lazy('anagrafica:elenco_rappresentanti')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Rappresentante {self.object} creato con successo!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Nuovo Rappresentante'
        return context


class RappresentanteUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    """Modifica rappresentante"""
    model = Rappresentante
    form_class = RappresentanteForm
    template_name = 'anagrafica/rappresentanti/modifica.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Rappresentante {self.object} aggiornato con successo!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Modifica: {self.object}'
        return context


class RappresentanteDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    """Eliminazione rappresentante"""
    model = Rappresentante
    template_name = 'anagrafica/rappresentanti/elimina.html'
    success_url = reverse_lazy('anagrafica:elenco_rappresentanti')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        messages.success(request, f'Rappresentante {self.object} eliminato con successo!')
        return super().delete(request, *args, **kwargs)


# ================== CLIENTI ==================

class ClienteListView(LoginRequiredMixin, RappresentanteAccessMixin, ListView):
    """Lista clienti"""
    model = Cliente
    template_name = 'anagrafica/clienti/elenco.html'
    context_object_name = 'clienti'
    paginate_by = 20

    def get_queryset(self):
        queryset = Cliente.objects.select_related('rappresentante').order_by('-created_at')
        
        # Se l'utente è un rappresentante, mostra solo i suoi clienti
        if hasattr(self.request.user, 'rappresentante') and not self.request.user.is_staff:
            queryset = queryset.filter(rappresentante=self.request.user.rappresentante)
        
        # Filtri di ricerca
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(nome__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(telefono__icontains=search_query)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Elenco Clienti'
        context['search_query'] = self.request.GET.get('search', '')
        return context


class ClienteDetailView(LoginRequiredMixin, RappresentanteAccessMixin, DetailView):
    """Dettaglio cliente"""
    model = Cliente
    template_name = 'anagrafica/clienti/dettaglio.html'
    context_object_name = 'cliente'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Cliente: {self.object.nome}'
        return context


class ClienteCreateView(LoginRequiredMixin, CreateView):
    """Creazione cliente (SENZA sconto percentuale)"""
    model = Cliente
    form_class = ClienteForm
    template_name = 'anagrafica/clienti/nuovo.html'
    success_url = reverse_lazy('anagrafica:elenco_clienti')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Se l'utente è un rappresentante, assegna automaticamente
        if hasattr(self.request.user, 'rappresentante') and not self.request.user.is_staff:
            form.instance.rappresentante = self.request.user.rappresentante
        
        response = super().form_valid(form)
        messages.success(self.request, f'Cliente {self.object.nome} creato con successo!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Nuovo Cliente'
        return context


class ClienteUpdateView(LoginRequiredMixin, RappresentanteAccessMixin, UpdateView):
    """Modifica cliente"""
    model = Cliente
    form_class = ClienteForm
    template_name = 'anagrafica/clienti/modifica.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Cliente {self.object.nome} aggiornato con successo!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Modifica: {self.object.nome}'
        return context


class ClienteDeleteView(LoginRequiredMixin, RappresentanteAccessMixin, DeleteView):
    """Eliminazione cliente"""
    model = Cliente
    template_name = 'anagrafica/clienti/elimina.html'
    success_url = reverse_lazy('anagrafica:elenco_clienti')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        messages.success(request, f'Cliente {self.object.nome} eliminato con successo!')
        return super().delete(request, *args, **kwargs)


# ================== FORNITORI ==================

class FornitoreListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """Lista fornitori"""
    model = Fornitore
    template_name = 'anagrafica/fornitori/elenco.html'
    context_object_name = 'fornitori'
    paginate_by = 20

    def get_queryset(self):
        queryset = Fornitore.objects.order_by('-created_at')
        
        # Filtri di ricerca
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(nome__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(telefono__icontains=search_query)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Elenco Fornitori'
        context['search_query'] = self.request.GET.get('search', '')
        return context


class FornitoreDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    """Dettaglio fornitore"""
    model = Fornitore
    template_name = 'anagrafica/fornitori/dettaglio.html'
    context_object_name = 'fornitore'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Fornitore: {self.object.nome}'
        return context


class FornitoreCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """Creazione fornitore"""
    model = Fornitore
    form_class = FornitoreForm
    template_name = 'anagrafica/fornitori/nuovo.html'
    success_url = reverse_lazy('anagrafica:elenco_fornitori')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Fornitore {self.object.nome} creato con successo!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Nuovo Fornitore'
        return context


class FornitoreUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    """Modifica fornitore"""
    model = Fornitore
    form_class = FornitoreForm
    template_name = 'anagrafica/fornitori/modifica.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Fornitore {self.object.nome} aggiornato con successo!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Modifica: {self.object.nome}'
        return context


class FornitoreDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    """Eliminazione fornitore"""
    model = Fornitore
    template_name = 'anagrafica/fornitori/elimina.html'
    success_url = reverse_lazy('anagrafica:elenco_fornitori')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        messages.success(request, f'Fornitore {self.object.nome} eliminato con successo!')
        return super().delete(request, *args, **kwargs)


# ================== API E UTILITIES ==================

@login_required
def api_search_anagrafica(request):
    """API per ricerca nell'anagrafica"""
    query = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '')
    
    results = []
    
    if len(query) >= 2:
        # Cerca nei rappresentanti
        if not tipo or tipo == 'rappresentanti':
            rappresentanti = Rappresentante.objects.filter(
                Q(nome__icontains=query) |
                Q(cognome__icontains=query) |
                Q(email__icontains=query) |
                Q(telefono__icontains=query)
            )[:10]
            
            for r in rappresentanti:
                results.append({
                    'tipo': 'rappresentante',
                    'id': r.id,
                    'nome': str(r),
                    'email': r.email,
                    'telefono': r.telefono,
                    'url': r.get_absolute_url()
                })
        
        # Cerca nei clienti
        if not tipo or tipo == 'clienti':
            clienti_qs = Cliente.objects.filter(
                Q(nome__icontains=query) |
                Q(email__icontains=query) |
                Q(telefono__icontains=query)
            )
            
            # Se l'utente è un rappresentante, limita ai suoi clienti
            if hasattr(request.user, 'rappresentante') and not request.user.is_staff:
                clienti_qs = clienti_qs.filter(rappresentante=request.user.rappresentante)
            
            clienti = clienti_qs[:10]
            
            for c in clienti:
                results.append({
                    'tipo': 'cliente',
                    'id': c.id,
                    'nome': c.nome,
                    'email': c.email,
                    'telefono': c.telefono,
                    'url': c.get_absolute_url()
                })
        
        # Cerca nei fornitori (solo staff)
        if (not tipo or tipo == 'fornitori') and (request.user.is_staff or request.user.is_superuser):
            fornitori = Fornitore.objects.filter(
                Q(nome__icontains=query) |
                Q(email__icontains=query) |
                Q(telefono__icontains=query)
            )[:10]
            
            for f in fornitori:
                results.append({
                    'tipo': 'fornitore',
                    'id': f.id,
                    'nome': f.nome,
                    'email': f.email,
                    'telefono': f.telefono,
                    'url': f.get_absolute_url()
                })
    
    return JsonResponse({'results': results})


@login_required
def export_anagrafica(request):
    """Export dati anagrafica in CSV"""
    tipo = request.GET.get('tipo', 'clienti')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{tipo}_{request.user.id}.csv"'
    
    writer = csv.writer(response)
    
    if tipo == 'clienti':
        writer.writerow(['Nome', 'Email', 'Telefono', 'Rappresentante', 'Attivo'])
        clienti = Cliente.objects.select_related('rappresentante')
        
        if hasattr(request.user, 'rappresentante') and not request.user.is_staff:
            clienti = clienti.filter(rappresentante=request.user.rappresentante)
        
        for cliente in clienti:
            writer.writerow([
                cliente.nome,
                cliente.email,
                cliente.telefono,
                str(cliente.rappresentante) if cliente.rappresentante else '',
                'Sì' if cliente.attivo else 'No'
            ])
    
    elif tipo == 'fornitori' and (request.user.is_staff or request.user.is_superuser):
        writer.writerow(['Nome', 'Email', 'Telefono', 'Categoria', 'Attivo'])
        fornitori = Fornitore.objects.all()
        
        for fornitore in fornitori:
            writer.writerow([
                fornitore.nome,
                fornitore.email,
                fornitore.telefono,
                fornitore.get_categoria_display(),
                'Sì' if fornitore.attivo else 'No'
            ])
    
    return response


@login_required
def toggle_attivo(request, tipo, pk):
    """Toggle stato attivo/inattivo per entità anagrafica"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Non hai i permessi per questa operazione.')
        return redirect('anagrafica:dashboard')
    
    if tipo == 'rappresentante':
        obj = get_object_or_404(Rappresentante, pk=pk)
        obj.attivo = not obj.attivo
        obj.save()
        messages.success(request, f'Rappresentante {obj} {"attivato" if obj.attivo else "disattivato"}.')
        return redirect('anagrafica:elenco_rappresentanti')
    
    elif tipo == 'cliente':
        obj = get_object_or_404(Cliente, pk=pk)
        obj.attivo = not obj.attivo
        obj.save()
        messages.success(request, f'Cliente {obj.nome} {"attivato" if obj.attivo else "disattivato"}.')
        return redirect('anagrafica:elenco_clienti')
    
    elif tipo == 'fornitore':
        obj = get_object_or_404(Fornitore, pk=pk)
        obj.attivo = not obj.attivo
        obj.save()
        messages.success(request, f'Fornitore {obj.nome} {"attivato" if obj.attivo else "disattivato"}.')
        return redirect('anagrafica:elenco_fornitori')
    
    messages.error(request, 'Tipo non valido.')
    return redirect('anagrafica:dashboard')