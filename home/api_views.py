# home/api_views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils.formats import date_format
from .models import Messaggio

@login_required
@require_http_methods(["GET"])
def check_messages(request):
    """API endpoint per controllare i messaggi non letti"""
    user = request.user
    
    # Conta i messaggi non letti
    unread_count = Messaggio.objects.filter(
        destinatario=user,
        letto=False
    ).count()
    
    # Ottieni gli ultimi 5 messaggi
    messaggi_recenti = Messaggio.objects.filter(
        destinatario=user
    ).select_related('mittente').order_by('-data_invio')[:5]
    
    # Prepara i dati dei messaggi recenti
    messaggi_data = []
    for msg in messaggi_recenti:
        messaggi_data.append({
            'id': msg.id,
            'mittente_id': msg.mittente.id,
            'mittente_nome': msg.mittente.get_full_name() or msg.mittente.username,
            'testo': msg.testo[:45] + '...' if len(msg.testo) > 45 else msg.testo,
            'data_invio': date_format(msg.data_invio, 'd/m H:i'),
            'letto': msg.letto
        })
    
    # Ottieni l'ultimo messaggio non letto per la notifica desktop
    latest_message = None
    if unread_count > 0:
        latest_msg = Messaggio.objects.filter(
            destinatario=user,
            letto=False
        ).order_by('-data_invio').first()
        
        if latest_msg:
            latest_message = {
                'sender': latest_msg.mittente.get_full_name() or latest_msg.mittente.username,
                'text': latest_msg.testo,
                'date': latest_msg.data_invio.isoformat()
            }
    
    return JsonResponse({
        'unread_count': unread_count,
        'messaggi_recenti': messaggi_data,
        'latest_message': latest_message
    })

@login_required
@require_http_methods(["POST"])
def mark_message_read(request, message_id):
    """API endpoint per marcare un messaggio come letto"""
    try:
        messaggio = Messaggio.objects.get(id=message_id, destinatario=request.user)
        messaggio.letto = True
        messaggio.save()
        return JsonResponse({'success': True})
    except Messaggio.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Messaggio non trovato'}, status=404)