/* static/js/automezzi/automezzi.js */

// Funzione per calcolo automatico importo rifornimento
function calcolaImporto() {
    const litri = parseFloat(document.getElementById('id_litri').value) || 0;
    const prezzoLitro = parseFloat(document.getElementById('id_prezzo_litro').value) || 0;
    const importoTotale = litri * prezzoLitro;
    
    if (importoTotale > 0) {
        document.getElementById('id_importo_totale').value = importoTotale.toFixed(2);
    }
}

// Funzione per formattazione automatica targa in maiuscolo
function formatTarga(input) {
    input.value = input.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
}

// Funzione per calcolo automatico età veicolo
function calcolaEta() {
    const annoImmatricolazione = parseInt(document.getElementById('id_anno_immatricolazione').value);
    const annoCorrente = new Date().getFullYear();
    
    if (annoImmatricolazione && annoImmatricolazione > 1900) {
        const eta = annoCorrente - annoImmatricolazione;
        
        // Mostra l'età in un elemento se presente
        const etaElement = document.getElementById('eta-veicolo');
        if (etaElement) {
            etaElement.textContent = `${eta} anni`;
        }
    }
}

// Validazione km in tempo reale
function validaKm() {
    const kmAttuali = parseInt(document.getElementById('id_km_attuali').value) || 0;
    const kmUltimaManutenzione = parseInt(document.getElementById('id_km_ultima_manutenzione').value) || 0;
    
    const kmAttualiField = document.getElementById('id_km_attuali');
    const kmManutenzioneeField = document.getElementById('id_km_ultima_manutenzione');
    
    // Reset classi
    kmAttualiField.classList.remove('is-invalid');
    kmManutenzioneeField.classList.remove('is-invalid');
    
    if (kmUltimaManutenzione > kmAttuali && kmAttuali > 0) {
        kmManutenzioneeField.classList.add('is-invalid');
        
        // Mostra messaggio di errore
        const feedback = kmManutenzioneeField.nextElementSibling || document.createElement('div');
        feedback.className = 'invalid-feedback';
        feedback.textContent = 'I km dell\'ultima manutenzione non possono essere superiori ai km attuali';
        
        if (!kmManutenzioneeField.nextElementSibling) {
            kmManutenzioneeField.insertAdjacentElement('afterend', feedback);
        }
    }
}

// Funzione per aggiornare i campi del fornitore quando si cambia la carta carburante
function aggiornaFornitore() {
    const cartaSelect = document.getElementById('id_carta_carburante');
    const fornitoreSelect = document.getElementById('id_fornitore');
    
    if (cartaSelect && fornitoreSelect && cartaSelect.selectedOptions.length > 0) {
        const selectedOption = cartaSelect.selectedOptions[0];
        const fornitoreId = selectedOption.getAttribute('data-fornitore-id');
        
        if (fornitoreId) {
            fornitoreSelect.value = fornitoreId;
        }
    }
}

// Funzione per mostrare/nascondere campo motivo blocco
function toggleMotivoBlocco() {
    const bloccataCheckbox = document.getElementById('id_bloccata');
    const motivoBloccoField = document.getElementById('id_motivo_blocco').closest('.form-group');
    
    if (bloccataCheckbox && motivoBloccoField) {
        if (bloccataCheckbox.checked) {
            motivoBloccoField.style.display = 'block';
            document.getElementById('id_motivo_blocco').required = true;
        } else {
            motivoBloccoField.style.display = 'none';
            document.getElementById('id_motivo_blocco').required = false;
            document.getElementById('id_motivo_blocco').value = '';
        }
    }
}

// Funzione per calcolo consumo in tempo reale
function calcolaConsumo() {
    const kmParziale = parseInt(document.getElementById('id_km_parziale').value) || 0;
    const litri = parseFloat(document.getElementById('id_litri').value) || 0;
    
    if (kmParziale > 0 && litri > 0) {
        const consumo = (kmParziale / litri).toFixed(2);
        
        // Mostra il consumo se c'è un elemento dedicato
        const consumoElement = document.getElementById('consumo-calcolato');
        if (consumoElement) {
            consumoElement.textContent = `${consumo} km/l`;
        }
        
        // Aggiunge una classe per evidenziare valori anomali
        if (parseFloat(consumo) < 5 || parseFloat(consumo) > 30) {
            consumoElement?.classList.add('text-warning');
        } else {
            consumoElement?.classList.remove('text-warning');
        }
    }
}

// Funzione per validazione IBAN
function validaIBAN(iban) {
    // Rimuove spazi e converte in maiuscolo
    iban = iban.replace(/\s/g, '').toUpperCase();
    
    // Formato base IBAN italiano
    const ibanRegex = /^IT\d{2}[A-Z]\d{10}[A-Z0-9]{12}$/;
    
    return ibanRegex.test(iban);
}

// Inizializzazione quando il DOM è pronto
document.addEventListener('DOMContentLoaded', function() {
    // Event listeners per la targa
    const targaField = document.getElementById('id_targa');
    if (targaField) {
        targaField.addEventListener('input', function() {
            formatTarga(this);
        });
    }
    
    // Event listeners per anno immatricolazione
    const annoField = document.getElementById('id_anno_immatricolazione');
    if (annoField) {
        annoField.addEventListener('change', calcolaEta);
        calcolaEta(); // Calcola subito se c'è già un valore
    }
    
    // Event listeners per km
    const kmAttualiField = document.getElementById('id_km_attuali');
    const kmManutenzioneeField = document.getElementById('id_km_ultima_manutenzione');
    
    if (kmAttualiField) {
        kmAttualiField.addEventListener('change', validaKm);
    }
    if (kmManutenzioneeField) {
        kmManutenzioneeField.addEventListener('change', validaKm);
    }
    
    // Event listeners per rifornimenti
    const litriField = document.getElementById('id_litri');
    const prezzoLitroField = document.getElementById('id_prezzo_litro');
    const kmParzialeField = document.getElementById('id_km_parziale');
    
    if (litriField) {
        litriField.addEventListener('change', function() {
            calcolaImporto();
            calcolaConsumo();
        });
    }
    
    if (prezzoLitroField) {
        prezzoLitroField.addEventListener('change', calcolaImporto);
    }
    
    if (kmParzialeField) {
        kmParzialeField.addEventListener('change', calcolaConsumo);
    }
    
    // Event listener per carta carburante
    const cartaCarburanteField = document.getElementById('id_carta_carburante');
    if (cartaCarburanteField) {
        cartaCarburanteField.addEventListener('change', aggiornaFornitore);
    }
    
    // Event listener per blocco carta
    const bloccataField = document.getElementById('id_bloccata');
    if (bloccataField) {
        bloccataField.addEventListener('change', toggleMotivoBlocco);
        toggleMotivoBlocco(); // Esegui subito per lo stato iniziale
    }
    
    // Validazione form al submit
    const forms = document.querySelectorAll('form[data-validate="true"]');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            
            // Validazioni specifiche per ogni tipo di form
            if (form.id === 'automezzo-form') {
                isValid = validaFormAutomezzo();
            } else if (form.id === 'rifornimento-form') {
                isValid = validaFormRifornimento();
            }
            
            if (!isValid) {
                e.preventDefault();
                e.stopPropagation();
            }
        });
    });
});

// Validazione specifica per form automezzo
function validaFormAutomezzo() {
    let isValid = true;
    
    // Controlla se assegnato ma senza data
    const assegnatoA = document.getElementById('id_assegnato_a').value;
    const dataAssegnazione = document.getElementById('id_data_assegnazione').value;
    
    if (assegnatoA && !dataAssegnazione) {
        document.getElementById('id_data_assegnazione').classList.add('is-invalid');
        isValid = false;
    }
    
    // Controlla alienazione
    const dataAlienazione = document.getElementById('id_data_alienazione').value;
    const valoreAlienazione = document.getElementById('id_valore_alienazione').value;
    const acquirente = document.getElementById('id_acquirente').value;
    
    if (dataAlienazione && !valoreAlienazione) {
        document.getElementById('id_valore_alienazione').classList.add('is-invalid');
        isValid = false;
    }
    
    if (dataAlienazione && !acquirente) {
        document.getElementById('id_acquirente').classList.add('is-invalid');
        isValid = false;
    }
    
    return isValid;
}

// Validazione specifica per form rifornimento
function validaFormRifornimento() {
    let isValid = true;
    
    // Verifica che litri e prezzo siano inseriti
    const litri = document.getElementById('id_litri').value;
    const prezzoLitro = document.getElementById('id_prezzo_litro').value;
    
    if (!litri || parseFloat(litri) <= 0) {
        document.getElementById('id_litri').classList.add('is-invalid');
        isValid = false;
    }
    
    if (!prezzoLitro || parseFloat(prezzoLitro) <= 0) {
        document.getElementById('id_prezzo_litro').classList.add('is-invalid');
        isValid = false;
    }
    
    // Verifica km totale se presente km parziale
    const kmParziale = document.getElementById('id_km_parziale').value;
    const kmTotale = document.getElementById('id_km_totale').value;
    
    if (kmParziale && !kmTotale) {
        document.getElementById('id_km_totale').classList.add('is-invalid');
        isValid = false;
    }
    
    return isValid;
}

// Funzione per highlight dei campi obbligatori quando vuoti
function highlightCampiObbligatori() {
    const campiObbligatori = document.querySelectorAll('input[required], select[required], textarea[required]');
    
    campiObbligatori.forEach(function(campo) {
        campo.addEventListener('blur', function() {
            if (!this.value) {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
            }
        });
    });
}

// Auto-complete per distributori di carburante
function initDistributoriAutocomplete() {
    const distributoreField = document.getElementById('id_distributore');
    if (!distributoreField) return;
    
    // Lista comuni distributori (puoi espandere questa lista)
    const distributoriComuni = [
        'Agip/Eni',
        'IP',
        'Q8',
        'Tamoil',
        'Esso',
        'Shell',
        'Total/Erg',
        'Repsol',
        'Keropetrol',
        'Italiana Petroli'
    ];
    
    // Crea datalist per autocomplete
    const datalist = document.createElement('datalist');
    datalist.id = 'distributori-list';
    
    distributoriComuni.forEach(distributore => {
        const option = document.createElement('option');
        option.value = distributore;
        datalist.appendChild(option);
    });
    
    document.body.appendChild(datalist);
    distributoreField.setAttribute('list', 'distributori-list');
}

// Chiamate di inizializzazione
document.addEventListener('DOMContentLoaded', function() {
    highlightCampiObbligatori();
    initDistributoriAutocomplete();
});