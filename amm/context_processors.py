# amm/context_processors.py
from datetime import datetime
import locale
from django.utils import timezone

def datetime_info(request):
    """
    Fornisce informazioni su data e ora correnti in formato italiano
    """
    # Imposta locale italiano
    try:
        locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'it_IT')
        except:
            pass
    
    now = datetime.now()
    return {
        'today_day': now.strftime('%A'),
        'today_date': now.strftime('%d %B %Y'),
        'current_time': now.strftime('%H:%M:%S'),
        # Aggiungiamo anche questi per compatibilità con il sistema
        'ora_corrente': now.strftime("%H:%M"),
        'data_corrente': now.strftime("%d/%m/%Y"),
        'datetime_corrente': timezone.now(),
    }

def messages_processor(request):
    """
    Fornisce i messaggi non letti per la navbar
    """
    context = {
        'messaggi_non_letti': 0,
        'messaggi_recenti': []
    }
    
    if request.user.is_authenticated:
        try:
            from home.models import Messaggio
            
            # Messaggi non letti
            messaggi_non_letti = Messaggio.objects.filter(
                destinatario=request.user,
                letto=False
            ).count()
            
            # Messaggi recenti (ultimi 5)
            messaggi_recenti = Messaggio.objects.filter(
                destinatario=request.user
            ).order_by('-data_invio')[:5]
            
            context.update({
                'messaggi_non_letti': messaggi_non_letti,
                'messaggi_recenti': messaggi_recenti,
            })
        except Exception as e:
            # Log l'errore ma non bloccare il rendering della pagina
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Errore nel caricamento messaggi: {e}")
    
    return context

# Funzione alternativa per compatibilità
def datetime_context(request):
    """Alias per datetime_info"""
    return datetime_info(request)

def messaggi_context(request):
    """Alias per messages_processor"""
    return messages_processor(request)