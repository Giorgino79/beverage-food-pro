from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from dipendenti.models import Dipendente
from .models import Messaggio, Promemoria  # Importa dai modelli dell'app home
from .forms import MessaggioForm, PromemoriaForm  # Importa dai form dell'app home

@login_required
def index(request):
    """
    Vista per la dashboard principale del sistema
    """
    user = request.user
    
    # Ottieni i messaggi recenti
    messaggi_ricevuti = Messaggio.objects.filter(destinatario=user).order_by('-data_invio')[:5]
    
    # Ottieni i promemoria dell'utente
    promemoria = Promemoria.objects.filter(
        Q(assegnato_a=user) & 
        (Q(completato=False) | Q(data_completamento__gte=timezone.now() - timezone.timedelta(days=7)))
    ).order_by('completato', 'data_scadenza')[:5]
    
    # Calcola promemoria attivi e scaduti per la dashboard
    promemoria_attivi = Promemoria.objects.filter(assegnato_a=user, completato=False).count()
    promemoria_scaduti = Promemoria.objects.filter(
        assegnato_a=user, 
        completato=False, 
        data_scadenza__lt=timezone.now().date()
    ).count()
    
    # Ottieni i dipendenti online
    dipendenti_online = Dipendente.objects.filter(is_active=True, is_online=True).exclude(id=user.id)
    
    # Numero di messaggi non letti
    messaggi_non_letti = Messaggio.objects.filter(destinatario=user, letto=False).count()
    
    context = {
        'page_title': 'Dashboard',
        'messaggi_ricevuti': messaggi_ricevuti,
        'promemoria': promemoria,
        'promemoria_attivi': promemoria_attivi,
        'promemoria_scaduti': promemoria_scaduti,
        'dipendenti_online': dipendenti_online,
        'messaggi_non_letti': messaggi_non_letti,
    }
    
    return render(request, 'home/dashboard.html', context)

def landing_page(request):
    """
    Vista per la pagina di landing
    Se l'utente è già autenticato, reindirizzalo alla dashboard
    """
    if request.user.is_authenticated:
        return redirect('home:index')
    
    # Context per la landing page
    context = {
        'page_title': 'Benvenuto',
       
    }
    
    return render(request, 'home/landing_page.html', context)

# home/views.py - Vista chat aggiornata
@login_required
def chat(request):
    """Vista per la chat e l'invio messaggi"""
    user = request.user
    
    # Gestione form per nuovo messaggio
    if request.method == 'POST':
        form = MessaggioForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            messaggio = form.save(commit=False)
            messaggio.mittente = user
            messaggio.save()
            
            messages.success(request, _('Messaggio inviato con successo a {}').format(
                messaggio.destinatario.get_full_name() or messaggio.destinatario.username
            ))
            return redirect('home:chat')
    else:
        form = MessaggioForm(user=user)
    
    # Ottieni tutti i messaggi dell'utente (ricevuti e inviati)
    messaggi_ricevuti = Messaggio.objects.filter(destinatario=user).order_by('-data_invio')
    messaggi_inviati = Messaggio.objects.filter(mittente=user).order_by('-data_invio')
    
    # Ottieni la lista degli utenti con cui c'è stata una conversazione
    contatti_ids = set(
        list(messaggi_ricevuti.values_list('mittente_id', flat=True)) + 
        list(messaggi_inviati.values_list('destinatario_id', flat=True))
    )
    contatti = Dipendente.objects.filter(id__in=contatti_ids)
    
    # Se è specificato un contatto, filtra la conversazione
    contatto_id = request.GET.get('contatto')
    conversazione_filtrata = None
    contatto_selezionato = None
    
    if contatto_id:
        try:
            contatto_selezionato = Dipendente.objects.get(pk=contatto_id)
            conversazione_filtrata = Messaggio.objects.filter(
                (Q(mittente=user) & Q(destinatario=contatto_selezionato)) | 
                (Q(mittente=contatto_selezionato) & Q(destinatario=user))
            ).order_by('data_invio')
            
            # IMPORTANTE: Marca i messaggi non letti di questo contatto come letti
            messaggi_non_letti = conversazione_filtrata.filter(
                destinatario=user, 
                mittente=contatto_selezionato,
                letto=False
            )
            messaggi_non_letti.update(letto=True)
        except (Dipendente.DoesNotExist, ValueError):
            pass
    
    context = {
        'form': form,
        'messaggi_ricevuti': messaggi_ricevuti,
        'messaggi_inviati': messaggi_inviati,
        'contatti': contatti,
        'conversazione': conversazione_filtrata,
        'contatto_selezionato': contatto_selezionato,
    }
    
    return render(request, 'home/chat.html', context)

@login_required
def promemoria_list(request):
    """Vista per la lista dei promemoria"""
    user = request.user
    
    # Filtra i promemoria in base al tipo di utente
    if user.is_staff or user.is_superuser or (hasattr(user, 'livello') and user.livello == Dipendente.Autorizzazioni.totale):
        promemoria = Promemoria.objects.all()
    else:
        promemoria = Promemoria.objects.filter(
            Q(assegnato_a=user) | Q(creato_da=user)
        )
    
    # Filtra per stato (completato/da fare)
    stato = request.GET.get('stato')
    if stato == 'completati':
        promemoria = promemoria.filter(completato=True)
    elif stato == 'attivi':
        promemoria = promemoria.filter(completato=False)
    
    # Conta i promemoria attivi e completati per le statistiche
    promemoria_attivi = promemoria.filter(completato=False).count()
    promemoria_completati = promemoria.filter(completato=True).count()
    
    # Ordina i promemoria
    promemoria = promemoria.order_by('completato', 'data_scadenza')
    
    context = {
        'promemoria': promemoria,
        'stato_attuale': stato,
        'promemoria_attivi': promemoria_attivi,
        'promemoria_completati': promemoria_completati,
    }
    
    return render(request, 'home/promemoria_list.html', context)

@login_required
def promemoria_create(request):
    """Vista per la creazione di un nuovo promemoria"""
    if request.method == 'POST':
        form = PromemoriaForm(request.POST, user=request.user)
        if form.is_valid():
            promemoria = form.save(commit=False)
            promemoria.creato_da = request.user
            promemoria.save()
            
            messages.success(request, _('Promemoria creato con successo!'))
            return redirect('home:promemoria_list')
    else:
        form = PromemoriaForm(user=request.user)
    
    context = {
        'form': form,
        'is_update': False,
    }
    
    return render(request, 'home/promemoria_form.html', context)

@login_required
def promemoria_update(request, pk):
    """Vista per l'aggiornamento di un promemoria esistente"""
    promemoria = get_object_or_404(Promemoria, pk=pk)
    
    # Verifica che l'utente possa modificare il promemoria
    if not (request.user.is_staff or request.user.is_superuser or request.user == promemoria.creato_da):
        messages.error(request, _('Non hai i permessi per modificare questo promemoria.'))
        return redirect('home:promemoria_list')
    
    if request.method == 'POST':
        form = PromemoriaForm(request.POST, instance=promemoria, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Promemoria aggiornato con successo!'))
            return redirect('home:promemoria_list')
    else:
        form = PromemoriaForm(instance=promemoria, user=request.user)
    
    context = {
        'form': form,
        'promemoria': promemoria,
        'is_update': True,
    }
    
    return render(request, 'home/promemoria_form.html', context)

@login_required
def promemoria_toggle(request, pk):
    """Vista per marcare un promemoria come completato/non completato"""
    promemoria = get_object_or_404(Promemoria, pk=pk)
    
    # Verifica che l'utente possa modificare lo stato del promemoria
    if not (request.user.is_staff or request.user.is_superuser or 
            request.user == promemoria.assegnato_a or request.user == promemoria.creato_da):
        messages.error(request, _('Non hai i permessi per modificare questo promemoria.'))
    else:
        promemoria.completato = not promemoria.completato
        if promemoria.completato:
            promemoria.data_completamento = timezone.now()
        else:
            promemoria.data_completamento = None
        promemoria.save()
        
        status = 'completato' if promemoria.completato else 'riaperto'
        messages.success(request, _(f'Promemoria {status} con successo!'))
    
    next_url = request.GET.get('next', 'home:promemoria_list')
    return redirect(next_url)

@login_required
def promemoria_delete(request, pk):
    """Vista per eliminare un promemoria"""
    promemoria = get_object_or_404(Promemoria, pk=pk)
    
    # Verifica che l'utente possa eliminare il promemoria
    if not (request.user.is_staff or request.user.is_superuser or 
            (hasattr(request.user, 'livello') and request.user.livello == Dipendente.Autorizzazioni.totale) or 
            request.user == promemoria.creato_da):
        messages.error(request, _('Non hai i permessi per eliminare questo promemoria.'))
        return redirect('home:promemoria_list')
    
    if request.method == 'POST':
        promemoria.delete()
        messages.success(request, _('Promemoria eliminato con successo!'))
        return redirect('home:promemoria_list')
    
    context = {
        'promemoria': promemoria,
    }
    
    return render(request, 'home/promemoria_delete.html', context)

# home/views.py - Aggiungi questa vista
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

@login_required
def global_search(request):
    """
    Vista per la ricerca globale nel sistema
    Cerca in dipendenti, messaggi, promemoria
    """
    query = request.GET.get('q', '').strip()
    results = {
        'dipendenti': [],
        'messaggi': [],
        'promemoria': [],
        'query': query,
        'total_results': 0
    }
    
    if query and len(query) >= 2:  # Cerca solo se almeno 2 caratteri
        User = get_user_model()
        
        # Cerca nei dipendenti
        dipendenti_results = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(CF__icontains=query)
        ).exclude(id=request.user.id)  # Escludi te stesso
        
        # Cerca nei messaggi
        messaggi_results = Messaggio.objects.filter(
            Q(testo__icontains=query) |
            Q(mittente__username__icontains=query) |
            Q(destinatario__username__icontains=query)
        ).filter(
            Q(mittente=request.user) | Q(destinatario=request.user)
        ).distinct().order_by('-data_invio')
        
        # Cerca nei promemoria (se l'app esiste)
        promemoria_results = []
        try:
            promemoria_results = Promemoria.objects.filter(
                Q(titolo__icontains=query) |
                Q(descrizione__icontains=query) |
                Q(assegnato_a__username__icontains=query) |
                Q(creato_da__username__icontains=query)
            ).filter(
                Q(assegnato_a=request.user) | Q(creato_da=request.user)
            ).order_by('-data_scadenza')
        except:
            pass  # Se il modello Promemoria non esiste ancora
        
        # Limita i risultati per categoria
        results['dipendenti'] = dipendenti_results[:10]
        results['messaggi'] = messaggi_results[:10]
        results['promemoria'] = promemoria_results[:10]
        results['total_results'] = (
            dipendenti_results.count() + 
            messaggi_results.count() + 
            len(promemoria_results)
        )
    
    context = {
        'results': results,
        'page_title': f'Risultati ricerca: {query}' if query else 'Ricerca'
    }
    
    return render(request, 'home/search_results.html', context)

# home/views.py - Aggiungi questa vista per la ricerca rapida
from django.http import JsonResponse

@login_required
def quick_search(request):
    """API per ricerca rapida con autocomplete"""
    query = request.GET.get('q', '').strip()
    results = []
    
    if query and len(query) >= 2:
        User = get_user_model()
        
        # Cerca 3 dipendenti
        dipendenti = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(id=request.user.id)[:3]
        
        for dipendente in dipendenti:
            results.append({
                'type': 'dipendente',
                'id': dipendente.id,
                'title': dipendente.get_full_name() or dipendente.username,
                'subtitle': f"{dipendente.email} - {dipendente.get_livello_display()}"
            })
        
        # Cerca 3 messaggi recenti
        messaggi = Messaggio.objects.filter(
            Q(testo__icontains=query)
        ).filter(
            Q(mittente=request.user) | Q(destinatario=request.user)
        ).order_by('-data_invio')[:3]
        
        for messaggio in messaggi:
            results.append({
                'type': 'messaggio',
                'id': messaggio.id,
                'extra': messaggio.mittente.id if messaggio.mittente != request.user else messaggio.destinatario.id,
                'title': f"Messaggio da/a {messaggio.mittente.username if messaggio.mittente != request.user else messaggio.destinatario.username}",
                'subtitle': messaggio.testo[:50] + '...'
            })
        
        # Cerca 2 promemoria
        try:
            promemoria = Promemoria.objects.filter(
                Q(titolo__icontains=query) | Q(descrizione__icontains=query)
            ).filter(
                Q(assegnato_a=request.user) | Q(creato_da=request.user)
            )[:2]
            
            for p in promemoria:
                results.append({
                    'type': 'promemoria',
                    'id': p.id,
                    'title': p.titolo,
                    'subtitle': f"Scadenza: {p.data_scadenza.strftime('%d/%m/%Y')}"
                })
        except:
            pass
    
    return JsonResponse({'results': results})

# Aggiungi anche questo URL in home/urls.py:
# path('api/quick-search/', views.quick_search, name='quick_search'),