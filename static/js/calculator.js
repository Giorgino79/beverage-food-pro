// Aggiungi questo al file static/js/ui-improvements.js o crea un nuovo file static/js/calculator.js

// Logica della calcolatrice
document.addEventListener('DOMContentLoaded', function() {
    const calculatorModal = document.getElementById('calculatorModal');
    if (!calculatorModal) return;
    
    const screen = document.getElementById('calculatorScreen');
    const buttons = document.querySelectorAll('.calc-btn');
    
    let currentInput = '0';
    let operator = null;
    let waitingForNewNumber = false;
    let firstNumber = null;
    
    // Funzioni helper
    function updateScreen() {
        screen.value = currentInput;
    }
    
    function clear() {
        currentInput = '0';
        operator = null;
        waitingForNewNumber = false;
        firstNumber = null;
    }
    
    function clearEntry() {
        currentInput = '0';
    }
    
    function backspace() {
        if (currentInput.length > 1) {
            currentInput = currentInput.slice(0, -1);
        } else {
            currentInput = '0';
        }
    }
    
    function addNumber(num) {
        if (waitingForNewNumber) {
            currentInput = num;
            waitingForNewNumber = false;
        } else {
            currentInput = currentInput === '0' ? num : currentInput + num;
        }
    }
    
    function addDecimal() {
        if (waitingForNewNumber) {
            currentInput = '0.';
            waitingForNewNumber = false;
        } else if (currentInput.indexOf('.') === -1) {
            currentInput += '.';
        }
    }
    
    function setOperator(op) {
        if (firstNumber === null) {
            firstNumber = parseFloat(currentInput);
        } else if (operator && !waitingForNewNumber) {
            calculate();
        }
        
        operator = op;
        waitingForNewNumber = true;
    }
    
    function calculate() {
        if (operator && firstNumber !== null && !waitingForNewNumber) {
            const secondNumber = parseFloat(currentInput);
            let result;
            
            switch (operator) {
                case '+':
                    result = firstNumber + secondNumber;
                    break;
                case '-':
                    result = firstNumber - secondNumber;
                    break;
                case '*':
                    result = firstNumber * secondNumber;
                    break;
                case '/':
                    result = secondNumber !== 0 ? firstNumber / secondNumber : 'Error';
                    break;
                default:
                    return;
            }
            
            if (result === 'Error') {
                currentInput = 'Error';
                operator = null;
                firstNumber = null;
                waitingForNewNumber = true;
            } else {
                // Gestisci i decimali
                currentInput = result.toString();
                // Se il risultato ha troppe cifre decimali, arrotonda
                if (currentInput.includes('.') && currentInput.split('.')[1].length > 8) {
                    currentInput = result.toFixed(8).replace(/\.?0+$/, '');
                }
                operator = null;
                firstNumber = null;
                waitingForNewNumber = true;
            }
        }
    }
    
    // Event listeners per i pulsanti
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            const action = this.dataset.action;
            const value = this.dataset.value;
            
            switch (action) {
                case 'number':
                    addNumber(value);
                    break;
                case 'operator':
                    setOperator(value);
                    break;
                case 'decimal':
                    addDecimal();
                    break;
                case 'equals':
                    calculate();
                    break;
                case 'clear':
                    clear();
                    break;
                case 'clear-entry':
                    clearEntry();
                    break;
                case 'backspace':
                    backspace();
                    break;
            }
            
            updateScreen();
        });
    });
    
    // Gestione della tastiera
    document.addEventListener('keydown', function(e) {
        if (!calculatorModal.classList.contains('show')) return;
        
        const key = e.key;
        
        // Numeri
        if (/[0-9]/.test(key)) {
            addNumber(key);
            updateScreen();
        }
        // Operatori
        else if (key === '+' || key === '-' || key === '*' || key === '/') {
            setOperator(key);
            updateScreen();
        }
        // Punto decimale
        else if (key === '.' || key === ',') {
            addDecimal();
            updateScreen();
        }
        // Uguale o Enter
        else if (key === '=' || key === 'Enter') {
            calculate();
            updateScreen();
        }
        // Escape o c per clear
        else if (key === 'Escape' || key.toLowerCase() === 'c') {
            clear();
            updateScreen();
        }
        // Backspace o Delete
        else if (key === 'Backspace' || key === 'Delete') {
            backspace();
            updateScreen();
        }
    });
    
    // Resetta la calcolatrice quando si chiude il modal
    calculatorModal.addEventListener('hidden.bs.modal', function () {
        clear();
        updateScreen();
    });
    
    // Focus sul modal quando si apre
    calculatorModal.addEventListener('shown.bs.modal', function () {
        calculatorModal.focus();
    });
});