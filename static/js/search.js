// static/js/search.js - Ricerca con autocomplete (opzionale)
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('globalSearchInput');
    let searchTimeout;
    
    if (searchInput) {
        // Crea un dropdown per i risultati rapidi
        const dropdown = document.createElement('div');
        dropdown.className = 'search-dropdown position-absolute bg-white border shadow-sm';
        dropdown.style.cssText = `
            top: 100%;
            left: 0;
            right: 0;
            max-height: 300px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
        `;
        searchInput.parentElement.appendChild(dropdown);
        
        // Funzione di ricerca rapida
        function quickSearch(query) {
            if (query.length < 2) {
                dropdown.style.display = 'none';
                return;
            }
            
            fetch(`/home/api/quick-search/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    dropdown.innerHTML = '';
                    
                    if (data.results && data.results.length > 0) {
                        data.results.forEach(item => {
                            const div = document.createElement('div');
                            div.className = 'p-2 border-bottom quick-search-item';
                            div.style.cursor = 'pointer';
                            
                            let icon = '';
                            let url = '';
                            
                            switch(item.type) {
                                case 'dipendente':
                                    icon = '<i class="fas fa-user text-primary me-2"></i>';
                                    url = `/dipendenti/vedi/${item.id}/`;
                                    break;
                                case 'messaggio':
                                    icon = '<i class="fas fa-comment text-success me-2"></i>';
                                    url = `/home/chat/?contatto=${item.extra}`;
                                    break;
                                case 'promemoria':
                                    icon = '<i class="fas fa-task text-warning me-2"></i>';
                                    url = `/home/promemoria/`;
                                    break;
                            }
                            
                            div.innerHTML = `
                                ${icon}
                                <span>${item.title}</span>
                                <small class="text-muted d-block">${item.subtitle}</small>
                            `;
                            
                            div.onclick = () => window.location.href = url;
                            dropdown.appendChild(div);
                        });
                        
                        // Aggiungi link "Vedi tutti i risultati"
                        const viewAll = document.createElement('div');
                        viewAll.className = 'p-2 bg-light text-center';
                        viewAll.innerHTML = `<a href="/home/search/?q=${encodeURIComponent(query)}" class="text-decoration-none">Vedi tutti i risultati</a>`;
                        dropdown.appendChild(viewAll);
                        
                        dropdown.style.display = 'block';
                    } else {
                        dropdown.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Errore nella ricerca:', error);
                    dropdown.style.display = 'none';
                });
        }
        
        // Event listeners
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => quickSearch(this.value), 300);
        });
        
        // Nascondi dropdown quando si clicca fuori
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.style.display = 'none';
            }
        });
        
        // Style per gli elementi hover
        const style = document.createElement('style');
        style.textContent = `
            .quick-search-item:hover {
                background-color: #f8f9fa;
            }
        `;
        document.head.appendChild(style);
    }
});