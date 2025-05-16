/**
 * Funzioni JavaScript specifiche per l'app dipendenti
 */

// Funzione per inizializzare i selettori dipendenti con Select2
function initDipendentiSelectors() {
    $('.dipendente-selector').select2({
        theme: 'bootstrap-5',
        placeholder: 'Seleziona un dipendente',
        allowClear: true,
        width: '100%'
    });
}

// Funzione per inizializzare i selettori di intervalli di date
function initDateRangePickers() {
    $('.daterange-picker').daterangepicker({
        locale: {
            format: 'DD/MM/YYYY',
            separator: ' - ',
            applyLabel: 'Applica',
            cancelLabel: 'Annulla',
            fromLabel: 'Da',
            toLabel: 'A',
            customRangeLabel: 'Personalizzato',
            weekLabel: 'S',
            daysOfWeek: ['Do', 'Lu', 'Ma', 'Me', 'Gi', 'Ve', 'Sa'],
            monthNames: ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre'],
            firstDay: 1
        },
        ranges: {
            'Oggi': [moment(), moment()],
            'Ieri': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
            'Ultimi 7 giorni': [moment().subtract(6, 'days'), moment()],
            'Ultimi 30 giorni': [moment().subtract(29, 'days'), moment()],
            'Questo mese': [moment().startOf('month'), moment().endOf('month')],
            'Mese scorso': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        }
    });
}

// Funzione per formattare ore e minuti
function formatHoursAndMinutes(totalMinutes) {
    if (isNaN(totalMinutes) || totalMinutes < 0) {
        return '00:00';
    }
    
    const hours = Math.floor(totalMinutes / 60);
    const minutes = totalMinutes % 60;
    
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
}

// Funzione per calcolare differenza tra orari
function calculateTimeDifference(startTime, endTime) {
    if (!startTime || !endTime) {
        return 0;
    }
    
    const [startHours, startMinutes] = startTime.split(':').map(Number);
    const [endHours, endMinutes] = endTime.split(':').map(Number);
    
    const startTotalMinutes = startHours * 60 + startMinutes;
    const endTotalMinutes = endHours * 60 + endMinutes;
    
    if (endTotalMinutes < startTotalMinutes) {
        return 0; // L'orario di fine è prima dell'orario di inizio
    }
    
    return endTotalMinutes - startTotalMinutes;
}

// Funzione per la preview dei file caricati
function setupFilePreview(inputId, previewContainerId) {
    const fileInput = document.getElementById(inputId);
    const previewContainer = document.getElementById(previewContainerId);
    
    if (!fileInput || !previewContainer) {
        return;
    }
    
    fileInput.addEventListener('change', function() {
        // Pulisci il container
        previewContainer.innerHTML = '';
        
        if (this.files && this.files[0]) {
            const file = this.files[0];
            
            // Crea elemento di anteprima
            const preview = document.createElement('div');
            preview.className = 'file-preview';
            
            // Aggiungi nome e dimensione del file
            const fileInfo = document.createElement('div');
            fileInfo.className = 'file-info';
            
            // Determina icona in base al tipo di file
            let iconClass = 'fas fa-file';
            const fileType = file.type;
            
            if (fileType.startsWith('image/')) {
                iconClass = 'fas fa-file-image';
                
                // Per immagini, mostra anche l'anteprima
                const img = document.createElement('img');
                img.className = 'img-thumbnail mt-2';
                img.style.maxHeight = '150px';
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    img.src = e.target.result;
                };
                reader.readAsDataURL(file);
                
                preview.appendChild(img);
            } else if (fileType === 'application/pdf') {
                iconClass = 'fas fa-file-pdf';
            } else if (fileType.includes('word')) {
                iconClass = 'fas fa-file-word';
            }
            
            fileInfo.innerHTML = `
                <i class="${iconClass} me-2"></i>
                <span>${file.name}</span>
                <small class="text-muted ms-2">(${formatFileSize(file.size)})</small>
            `;
            
            preview.appendChild(fileInfo);
            previewContainer.appendChild(preview);
            previewContainer.classList.remove('d-none');
        } else {
            previewContainer.classList.add('d-none');
        }
    });
}

// Formatta la dimensione del file in KB, MB, etc.
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Inizializza tutte le funzionalità quando il documento è pronto
document.addEventListener('DOMContentLoaded', function() {
    // Inizializza selettori Select2
    if (typeof($.fn.select2) !== 'undefined') {
        initDipendentiSelectors();
    }
    
    // Inizializza date range pickers
    if (typeof($.fn.daterangepicker) !== 'undefined') {
        initDateRangePickers();
    }
    
    // Inizializza preview file
    setupFilePreview('id_file', 'file-preview-container');
});