/**
 * File JavaScript per miglioramenti UX/UI del Sistema Gestionale Django
 */
document.addEventListener('DOMContentLoaded', function() {
    // Toggle sidebar collapse
    const sidebarToggleBtn = document.getElementById('sidebarToggle');
    if (sidebarToggleBtn) {
        sidebarToggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            document.body.classList.toggle('sidebar-toggled');
            document.querySelector('.sidebar').classList.toggle('sidebar-collapsed');
            
            // Salva lo stato nella localStorage
            const isSidebarCollapsed = document.querySelector('.sidebar').classList.contains('sidebar-collapsed');
            localStorage.setItem('sidebarCollapsed', isSidebarCollapsed);
        });
        
        // Ripristina lo stato del sidebar dal localStorage
        const storedSidebarState = localStorage.getItem('sidebarCollapsed');
        if (storedSidebarState === 'true') {
            document.body.classList.add('sidebar-toggled');
            document.querySelector('.sidebar').classList.add('sidebar-collapsed');
        }
    }
    
    // Inizializza tooltip di Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Gestione auto-ridimensionamento delle textarea
    const textareas = document.querySelectorAll('textarea.auto-resize');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
            if (this.scrollHeight > 150) {
                this.style.height = '150px';
                this.style.overflowY = 'auto';
            } else {
                this.style.overflowY = 'hidden';
            }
        });
        
        // Imposta l'altezza iniziale
        if (textarea.value) {
            textarea.dispatchEvent(new Event('input'));
        }
    });
    
    // Gestione file upload con preview
    const fileInputs = document.querySelectorAll('input[type="file"].file-upload');
    fileInputs.forEach(input => {
        const filePreviewContainer = document.querySelector(input.dataset.previewContainer);
        const fileNameElement = document.querySelector(input.dataset.fileNameElement);
        
        if (input && filePreviewContainer) {
            input.addEventListener('change', function() {
                // Aggiorna il nome del file
                if (fileNameElement) {
                    fileNameElement.textContent = this.files[0] ? this.files[0].name : '';
                }
                
                // Se è un'immagine, mostra l'anteprima
                if (this.files && this.files[0]) {
                    const file = this.files[0];
                    if (file.type.match('image.*')) {
                        const reader = new FileReader();
                        
                        reader.onload = function(e) {
                            filePreviewContainer.innerHTML = `
                                <div class="position-relative">
                                    <img src="${e.target.result}" class="img-fluid rounded" alt="Preview">
                                    <button type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0 m-1 remove-preview">
                                        <i class="fas fa-times"></i>
                                    </button>
                                </div>
                            `;
                            
                            // Aggiungi gestore per rimuovere l'anteprima
                            const removeBtn = filePreviewContainer.querySelector('.remove-preview');
                            if (removeBtn) {
                                removeBtn.addEventListener('click', function() {
                                    input.value = '';
                                    filePreviewContainer.innerHTML = '';
                                    if (fileNameElement) {
                                        fileNameElement.textContent = '';
                                    }
                                });
                            }
                        };
                        
                        reader.readAsDataURL(file);
                    } else {
                        // Se non è un'immagine, mostra un'icona di file generica
                        let fileIcon = 'fa-file';
                        
                        if (file.type.includes('pdf')) {
                            fileIcon = 'fa-file-pdf';
                        } else if (file.type.includes('word') || file.name.endsWith('.doc') || file.name.endsWith('.docx')) {
                            fileIcon = 'fa-file-word';
                        } else if (file.type.includes('excel') || file.name.endsWith('.xls') || file.name.endsWith('.xlsx')) {
                            fileIcon = 'fa-file-excel';
                        } else if (file.type.includes('zip') || file.type.includes('rar') || file.type.includes('7z')) {
                            fileIcon = 'fa-file-archive';
                        } else if (file.type.includes('text')) {
                            fileIcon = 'fa-file-alt';
                        }
                        
                        filePreviewContainer.innerHTML = `
                            <div class="text-center">
                                <i class="fas ${fileIcon} fa-3x text-secondary"></i>
                                <p class="mt-2">${file.name}</p>
                                <button type="button" class="btn btn-sm btn-danger remove-preview">
                                    <i class="fas fa-times"></i> Rimuovi
                                </button>
                            </div>
                        `;
                        
                        // Aggiungi gestore per rimuovere l'anteprima
                        const removeBtn = filePreviewContainer.querySelector('.remove-preview');
                        if (removeBtn) {
                            removeBtn.addEventListener('click', function() {
                                input.value = '';
                                filePreviewContainer.innerHTML = '';
                                if (fileNameElement) {
                                    fileNameElement.textContent = '';
                                }
                            });
                        }
                    }
                }
            });
        }
    });
    
    // Posiziona lo scroll all'ultimo messaggio nella chat
    const messagesContainer = document.querySelector('.messages-container');
    if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Gestione del click sulla riga nelle tabelle interattive
    const clickableRows = document.querySelectorAll('tr.clickable-row');
    clickableRows.forEach(row => {
        row.addEventListener('click', function() {
            window.location = this.dataset.href;
        });
    });
    
    // Animazione per nuovi elementi aggiunti dinamicamente
    const animatedItems = document.querySelectorAll('.fade-in');
    animatedItems.forEach(item => {
        item.classList.add('animated-item');
    });
    
    // Attiva il submenu corrente nel sidebar
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('.sidebar .nav-link');
    
    sidebarLinks.forEach(link => {
        const href = link.getAttribute('href');
        
        if (href && currentPath.startsWith(href)) {
            link.classList.add('active');
            
            // Se il link è in un collapse, espandi il collapse
            const parentCollapseEl = link.closest('.collapse');
            if (parentCollapseEl) {
                const collapseToggle = document.querySelector(`[data-bs-target="#${parentCollapseEl.id}"]`);
                if (collapseToggle) {
                    parentCollapseEl.classList.add('show');
                    collapseToggle.classList.remove('collapsed');
                    collapseToggle.setAttribute('aria-expanded', 'true');
                }
            }
        }
    });
});

// Funzione per controllare nuovi messaggi
function checkForNewMessages() {
    // Questa è una simulazione - in un'implementazione reale, faresti una chiamata AJAX
    // per controllare i nuovi messaggi sul server
    console.log('Controllo nuovi messaggi...');
    
    // Simulazione di un nuovo messaggio ogni 30 secondi (1/10 di probabilità)
    if (Math.random() < 0.1) {
        const notificheDropdown = document.getElementById('notificheDropdown');
        if (notificheDropdown) {
            // Aggiorna il badge delle notifiche
            let badge = notificheDropdown.querySelector('.badge');
            
            if (!badge) {
                // Crea il badge se non esiste
                badge = document.createElement('span');
                badge.className = 'position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger';
                notificheDropdown.appendChild(badge);
            }
            
            // Incrementa il contatore nel badge
            const currentCount = parseInt(badge.textContent) || 0;
            badge.textContent = currentCount + 1;
            
            // Aggiungi una notifica di sistema tramite toastr se disponibile
            if (typeof toastr !== 'undefined') {
                toastr.info('Hai ricevuto un nuovo messaggio', 'Notifica', {
                    timeOut: 5000,
                    closeButton: true,
                    progressBar: true
                });
            }
        }
    }
}

// Avvia il controllo dei messaggi ogni 30 secondi se l'utente è loggato
const isLoggedIn = document.body.classList.contains('logged-in');
if (isLoggedIn) {
    setInterval(checkForNewMessages, 30000);
}

// Funzioni helper
function formatDateTime(date) {
    const options = { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(date).toLocaleDateString('it-IT', options);
}

function formatDate(date) {
    const options = { day: '2-digit', month: '2-digit', year: 'numeric' };
    return new Date(date).toLocaleDateString('it-IT', options);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' }).format(amount);
}

// Classe helper per le notifiche toast personalizzate
class Notifica {
    static mostra(messaggio, tipo = 'info', durata = 3000) {
        const tipi = {
            'success': { icon: 'fa-check-circle', color: 'var(--success-color)' },
            'error': { icon: 'fa-exclamation-circle', color: 'var(--danger-color)' },
            'warning': { icon: 'fa-exclamation-triangle', color: 'var(--warning-color)' },
            'info': { icon: 'fa-info-circle', color: 'var(--info-color)' }
        };
        
        const tipoNotifica = tipi[tipo] || tipi.info;
        
        // Crea l'elemento toast
        const toast = document.createElement('div');
        toast.className = 'notifica-toast';
        toast.style.position = 'fixed';
        toast.style.bottom = '20px';
        toast.style.right = '20px';
        toast.style.minWidth = '300px';
        toast.style.maxWidth = '400px';
        toast.style.backgroundColor = 'white';
        toast.style.boxShadow = '0 0.5rem 1rem rgba(0, 0, 0, 0.15)';
        toast.style.borderRadius = '0.35rem';
        toast.style.borderLeft = `4px solid ${tipoNotifica.color}`;
        toast.style.padding = '1rem';
        toast.style.zIndex = '9999';
        toast.style.transform = 'translateY(100%)';
        toast.style.transition = 'transform 0.3s ease-out';
        
        // Contenuto del toast
        toast.innerHTML = `
            <div class="d-flex align-items-center">
                <div style="color: ${tipoNotifica.color}; margin-right: 10px;">
                    <i class="fas ${tipoNotifica.icon} fa-2x"></i>
                </div>
                <div style="flex-grow: 1;">
                    <div>${messaggio}</div>
                </div>
                <button type="button" style="background: none; border: none; font-size: 1.2rem; cursor: pointer; color: #adb5bd;" 
                        onclick="this.parentNode.parentNode.remove();">
                    &times;
                </button>
            </div>
        `;
        
        // Aggiungi al DOM
        document.body.appendChild(toast);
        
        // Anima l'entrata
        setTimeout(() => {
            toast.style.transform = 'translateY(0)';
        }, 10);
        
        // Imposta l'auto-chiusura
        setTimeout(() => {
            toast.style.transform = 'translateY(100%)';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, durata);
        
        return toast;
    }
    
    static successo(messaggio, durata = 3000) {
        return this.mostra(messaggio, 'success', durata);
    }
    
    static errore(messaggio, durata = 3000) {
        return this.mostra(messaggio, 'error', durata);
    }
    
    static avviso(messaggio, durata = 3000) {
        return this.mostra(messaggio, 'warning', durata);
    }
    
    static info(messaggio, durata = 3000) {
        return this.mostra(messaggio, 'info', durata);
    }
}

// Classe per la gestione della chat in tempo reale
class ChatManager {
    constructor(options = {}) {
        this.options = {
            messagesContainerSelector: '.messages-container',
            messageFormSelector: '.chat-input-form',
            messageTextareaSelector: 'textarea[name="testo"]',
            sendButtonSelector: '.btn-send',
            fileInputSelector: 'input[type="file"]',
            contactsContainerSelector: '.contacts-container',
            messageTemplate: this._getDefaultMessageTemplate(),
            refreshInterval: 10000, // 10 secondi
            ...options
        };
        
        this.messagesContainer = document.querySelector(this.options.messagesContainerSelector);
        this.messageForm = document.querySelector(this.options.messageFormSelector);
        this.messageTextarea = document.querySelector(this.options.messageTextareaSelector);
        this.sendButton = document.querySelector(this.options.sendButtonSelector);
        this.fileInput = document.querySelector(this.options.fileInputSelector);
        
        this.init();
    }
    
    init() {
        if (!this.messagesContainer) return;
        
        // Posiziona lo scroll all'ultimo messaggio
        this.scrollToBottom();
        
        // Ascolta gli eventi di submit del form
        if (this.messageForm) {
            this.messageForm.addEventListener('submit', (e) => {
                if (!this.messageTextarea.value.trim() && !this.fileInput.files.length) {
                    e.preventDefault();
                    return;
                }
                
                // Aggiungi classe per tracciare il messaggio come "in invio"
                const submitButton = this.messageForm.querySelector('button[type="submit"]');
                if (submitButton) {
                    submitButton.disabled = true;
                    submitButton.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i>';
                }
            });
        }
        
        // Inizia il controllo per nuovi messaggi
        this.startMessagePolling();
    }
    
    scrollToBottom() {
        if (this.messagesContainer) {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }
    }
    
    startMessagePolling() {
        // In un'applicazione reale, qui useresti WebSockets o long polling
        // ma per questa simulazione, faremo un semplice controllo periodico
        setInterval(() => {
            this.checkForNewMessages();
        }, this.options.refreshInterval);
    }
    
    checkForNewMessages() {
        // Questa è una simulazione - in un'implementazione reale, faresti una chiamata AJAX
        console.log('Controllando nuovi messaggi nella chat...');
        
        // Qui faresti una chiamata fetch per ottenere i nuovi messaggi
        // fetch('/api/chat/messaggi-nuovi/') ...
    }
    
    addMessage(message) {
        if (!this.messagesContainer) return;
        
        const messageElement = document.createElement('div');
        messageElement.className = `message-item ${message.isSent ? 'sent' : 'received'}`;
        messageElement.innerHTML = this.options.messageTemplate
            .replace('{CLASS}', message.isSent ? 'sent' : 'received')
            .replace('{TEXT}', message.text)
            .replace('{TIME}', message.time);
        
        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }
    
    _getDefaultMessageTemplate() {
        return `
            <div class="message-bubble {CLASS} p-3 shadow-sm">
                <div class="message-text">{TEXT}</div>
                <div class="message-time text-end mt-1">{TIME}</div>
            </div>
        `;
    }
}

// Classe per la gestione dei promemoria con drag and drop
class PromemoriaManager {
    constructor(options = {}) {
        this.options = {
            containerSelector: '.promemoria-container',
            itemSelector: '.promemoria-item',
            completedContainerSelector: '.promemoria-completati',
            pendingContainerSelector: '.promemoria-da-fare',
            completedClassName: 'promemoria-completato',
            dragHandleSelector: '.drag-handle',
            toggleCompletedUrl: '/api/promemoria/toggle/', // URL per il toggle via AJAX
            ...options
        };
        
        this.container = document.querySelector(this.options.containerSelector);
        this.items = document.querySelectorAll(this.options.itemSelector);
        this.completedContainer = document.querySelector(this.options.completedContainerSelector);
        this.pendingContainer = document.querySelector(this.options.pendingContainerSelector);
        
        this.init();
    }
    
    init() {
        if (!this.container) return;
        
        // Inizializza il drag and drop se disponibile
        if (typeof Sortable !== 'undefined') {
            this.initSortable();
        }
        
        // Ascolta i clic sui pulsanti di toggle
        this.items.forEach(item => {
            const toggleBtn = item.querySelector('.toggle-completed');
            if (toggleBtn) {
                toggleBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.toggleCompleted(item);
                });
            }
        });
    }
    
    initSortable() {
        // Inizializza il drag and drop per i container
        if (this.pendingContainer) {
            Sortable.create(this.pendingContainer, {
                group: 'promemoria',
                animation: 150,
                handle: this.options.dragHandleSelector,
                ghostClass: 'promemoria-ghost',
                chosenClass: 'promemoria-chosen',
                onEnd: (evt) => {
                    if (evt.to === this.completedContainer) {
                        this.toggleCompleted(evt.item, true);
                    }
                }
            });
        }
        
        if (this.completedContainer) {
            Sortable.create(this.completedContainer, {
                group: 'promemoria',
                animation: 150,
                handle: this.options.dragHandleSelector,
                ghostClass: 'promemoria-ghost',
                chosenClass: 'promemoria-chosen',
                onEnd: (evt) => {
                    if (evt.to === this.pendingContainer) {
                        this.toggleCompleted(evt.item, false);
                    }
                }
            });
        }
    }
    
    toggleCompleted(item, completed = null) {
        // Prendi l'ID dal data attribute
        const id = item.dataset.id;
        if (!id) return;
        
        // Se completed non è specificato, inverti lo stato attuale
        if (completed === null) {
            completed = !item.classList.contains(this.options.completedClassName);
        }
        
        // Aggiorna l'interfaccia
        if (completed) {
            item.classList.add(this.options.completedClassName);
            if (this.completedContainer && item.parentNode !== this.completedContainer) {
                this.completedContainer.appendChild(item);
            }
        } else {
            item.classList.remove(this.options.completedClassName);
            if (this.pendingContainer && item.parentNode !== this.pendingContainer) {
                this.pendingContainer.appendChild(item);
            }
        }
        
        // Invia l'aggiornamento al server
        this.updateServerState(id, completed);
    }
    
    updateServerState(id, completed) {
        // Qui utilizzeresti fetch per inviare l'aggiornamento al server
        // fetch(`${this.options.toggleCompletedUrl}${id}/`, { method: 'POST', ... })
        console.log(`Aggiornamento promemoria ${id} a ${completed ? 'completato' : 'da fare'}`);
    }
}

// Inizializza i gestori quando il documento è pronto
document.addEventListener('DOMContentLoaded', function() {
    // Inizializza il gestore della chat se ci troviamo nella pagina chat
    if (document.querySelector('.chat-container')) {
        const chatManager = new ChatManager();
    }
    
    // Inizializza il gestore dei promemoria se ci troviamo nella pagina promemoria
    if (document.querySelector('.promemoria-container')) {
        const promemoriaManager = new PromemoriaManager();
    }
});