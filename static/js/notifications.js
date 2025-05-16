// static/js/notifications.js
document.addEventListener('DOMContentLoaded', function() {
    // Controlla i messaggi ogni 30 secondi (solo come esempio, in produzione usa WebSockets)
    function checkForNewMessages() {
        fetch('/api/check-messages/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.unread_count > 0) {
                updateNotificationBadge(data.unread_count);
                
                // Mostra notifica se supportata dal browser
                if ('Notification' in window && Notification.permission === 'granted') {
                    if (data.latest_message) {
                        new Notification(`Nuovo messaggio da ${data.latest_message.sender}`, {
                            body: data.latest_message.text.substring(0, 50) + '...',
                            icon: '/static/img/message-icon.png'
                        });
                    }
                }
            } else {
                updateNotificationBadge(0);
            }
        })
        .catch(error => console.error('Errore nel controllo messaggi:', error));
    }
    
    // Aggiorna il badge delle notifiche
    function updateNotificationBadge(count) {
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            if (count > 0) {
                badge.style.display = 'flex';
                badge.textContent = count > 99 ? '99+' : count;
            } else {
                badge.style.display = 'none';
            }
        }
    }
    
    // Richiedi permesso per le notifiche
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
    
    // Controlla i messaggi ogni 30 secondi (in sviluppo)
    // In produzione, usa WebSockets o Server-Sent Events
    setInterval(checkForNewMessages, 30000);
    
    // Controlla immediatamente al caricamento della pagina
    checkForNewMessages();
});

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

// static/js/notifications.js
document.addEventListener('DOMContentLoaded', function() {
    let currentUnreadCount = parseInt(document.querySelector('.notification-badge')?.textContent || '0');
    
    // Funzione per controllare se ci sono nuovi messaggi
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
            if (data.unread_count !== currentUnreadCount) {
                // C'è un cambiamento nei messaggi non letti
                location.reload(); // Ricarica la pagina per aggiornare la navbar
            }
        })
        .catch(error => console.error('Errore nel controllo messaggi:', error));
    }
    
    // Controlla ogni 5 secondi (solo per test, in produzione usa un intervallo più lungo)
    setInterval(checkNewMessages, 5000);
    
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