// static/js/notifications-ajax.js
document.addEventListener('DOMContentLoaded', function() {
    let currentUnreadCount = 0;
    const notificationBadge = document.querySelector('.notification-badge');
    const notificationDropdown = document.querySelector('#notificheDropdown').nextElementSibling;
    
    // Aggiorna il badge delle notifiche
    function updateNotificationBadge(count) {
        if (count > 0) {
            if (!notificationBadge) {
                // Crea il badge se non esiste
                const badge = document.createElement('span');
                badge.className = 'notification-badge';
                document.querySelector('#notificheDropdown .fas').parentElement.appendChild(badge);
            }
            notificationBadge.style.display = 'flex';
            notificationBadge.textContent = count > 99 ? '99+' : count;
        } else {
            if (notificationBadge) {
                notificationBadge.style.display = 'none';
            }
        }
    }
    
    // Aggiorna il contenuto del dropdown delle notifiche
    function updateNotificationDropdown(messaggi) {
        let html = '';
        if (messaggi.length > 0) {
            messaggi.forEach(msg => {
                html += `
                    <li class="notification-item ${!msg.letto ? 'unread' : ''}">
                        <a class="dropdown-item" href="/home/chat/?contatto=${msg.mittente_id}">
                            <div class="d-flex justify-content-between align-items-start">
                                <div class="flex-grow-1">
                                    <strong>${msg.mittente_nome}</strong>
                                    <div class="text-muted small mt-1">${msg.testo}</div>
                                </div>
                                <div class="small text-muted ms-2" style="min-width: 60px;">
                                    ${msg.data_invio}
                                </div>
                            </div>
                            ${!msg.letto ? '<div class="unread-dot"></div>' : ''}
                        </a>
                    </li>
                `;
            });
        } else {
            html = '<li><span class="dropdown-item text-muted">Nessun messaggio</span></li>';
        }
        
        html += `
            <li><hr class="dropdown-divider"></li>
            <li>
                <a class="dropdown-item text-center fw-bold" href="/home/chat/">
                    <i class="fas fa-comments me-1"></i> Visualizza tutti i messaggi
                </a>
            </li>
        `;
        
        notificationDropdown.innerHTML = html;
    }
    
    // Controlla i nuovi messaggi
    function checkNewMessages() {
        fetch('{% url "home:api_check_messages" %}', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            // Aggiorna il badge
            updateNotificationBadge(data.unread_count);
            
            // Aggiorna il dropdown se ci sono messaggi
            if (data.messaggi_recenti) {
                updateNotificationDropdown(data.messaggi_recenti);
            }
            
            // Mostra notifica desktop se supportata
            if ('Notification' in window && Notification.permission === 'granted') {
                if (data.unread_count > currentUnreadCount && data.latest_message) {
                    new Notification(`Nuovo messaggio da ${data.latest_message.sender}`, {
                        body: data.latest_message.text.substring(0, 50) + '...',
                        icon: '/static/img/message-icon.png'
                    });
                }
            }
            
            currentUnreadCount = data.unread_count;
        })
        .catch(error => console.error('Errore nel controllo messaggi:', error));
    }
    
    // Richiedi permesso per le notifiche
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
    
    // Controlla i messaggi ogni 10 secondi
    setInterval(checkNewMessages, 10000);
    
    // Controlla immediatamente al caricamento
    checkNewMessages();
    
    // Utility function per ottenere il CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});