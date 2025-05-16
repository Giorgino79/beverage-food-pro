import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from django.test.utils import override_settings
from django.core.management import call_command

from dipendenti.models import Dipendente
from .models import Rappresentante, Cliente, Fornitore
from .forms import RappresentanteForm, ClienteForm, FornitoreForm

User = get_user_model()


class AnagraficaModelTests(TestCase):
    """Test per i modelli dell'anagrafica"""
    
    def setUp(self):
        """Setup per ogni test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_rappresentante_creation(self):
        """Test creazione rappresentante valido"""
        rappresentante = Rappresentante.objects.create(
            nome='Mario Rossi',
            ragione_sociale='Test SRL',
            indirizzo='Via Test 123',
            cap='20100',
            città='Milano',
            provincia='MI',
            partita_iva='12345678901',
            codice_fiscale='RSSMRA80A01F205Z',
            telefono='02-1234567',
            email='mario@test.com',
            zona='Nord',
            percentuale_sulle_vendite=5.0
        )
        
        self.assertEqual(str(rappresentante), 'Mario Rossi - Nord')
        self.assertTrue(rappresentante.attivo)
        self.assertIsNotNone(rappresentante.data_creazione)
    
    def test_partita_iva_validation(self):
        """Test validazione partita IVA"""
        rappresentante = Rappresentante(
            nome='Test',
            ragione_sociale='Test SRL',
            partita_iva='123',  # P.IVA non valida
            codice_fiscale='12345678901',
            telefono='123456789',
            email='test@test.com',
            percentuale_sulle_vendite=5.0
        )
        
        with self.assertRaises(ValidationError):
            rappresentante.full_clean()
    
    def test_codice_fiscale_validation(self):
        """Test validazione codice fiscale"""
        rappresentante = Rappresentante(
            nome='Test',
            ragione_sociale='Test SRL',
            partita_iva='12345678901',
            codice_fiscale='INVALID',  # CF non valido
            telefono='123456789',
            email='test@test.com',
            percentuale_sulle_vendite=5.0
        )
        
        with self.assertRaises(ValidationError):
            rappresentante.full_clean()
    
    def test_cliente_with_rappresentante(self):
        """Test creazione cliente con rappresentante"""
        rappresentante = Rappresentante.objects.create(
            nome='Mario Rossi',
            ragione_sociale='Test SRL',
            partita_iva='12345678901',
            codice_fiscale='RSSMRA80A01F205Z',
            telefono='123456789',
            email='mario@test.com',
            percentuale_sulle_vendite=5.0
        )
        
        cliente = Cliente.objects.create(
            rappresentante=rappresentante,
            ragione_sociale='Cliente Test SRL',
            indirizzo='Via Cliente 123',
            cap='20100',
            città='Milano',
            provincia='MI',
            codice_fiscale='12345678901',
            telefono='02-9876543',
            email='cliente@test.com'
        )
        
        self.assertEqual(cliente.rappresentante, rappresentante)
        self.assertIn(cliente, rappresentante.clienti.all())
    
    def test_cliente_without_piva_cf(self):
        """Test cliente senza P.IVA e CF (deve fallire)"""
        cliente = Cliente(
            ragione_sociale='Test',
            # Mancano sia partita_iva che codice_fiscale
            telefono='123456789',
            email='test@test.com'
        )
        
        with self.assertRaises(ValidationError):
            cliente.full_clean()
    
    def test_fornitore_iban_validation(self):
        """Test validazione IBAN fornitore"""
        fornitore = Fornitore(
            ragione_sociale='Fornitore Test SRL',
            codice_fiscale='12345678901',
            telefono='123456789',
            email='fornitore@test.com',
            iban='INVALID_IBAN'  # IBAN non valido
        )
        
        with self.assertRaises(ValidationError):
            fornitore.full_clean()
    
    def test_unique_together_constraints(self):
        """Test vincoli unique_together"""
        # Primo cliente
        Cliente.objects.create(
            ragione_sociale='Test 1',
            partita_iva='12345678901',
            codice_fiscale='12345678901',
            telefono='123456789',
            email='test1@test.com'
        )
        
        # Secondo cliente con stessa P.IVA (deve fallire)
        with self.assertRaises(Exception):  # IntegrityError
            Cliente.objects.create(
                ragione_sociale='Test 2',
                partita_iva='12345678901',  # Duplicato
                codice_fiscale='12345678901',  # Duplicato
                telefono='987654321',
                email='test2@test.com'
            )


class AnagraficaFormTests(TestCase):
    """Test per i form dell'anagrafica"""
    
    def test_rappresentante_form_valid(self):
        """Test form rappresentante valido"""
        form_data = {
            'nome': 'Mario Rossi',
            'ragione_sociale': 'Test SRL',
            'indirizzo': 'Via Test 123',
            'cap': '20100',
            'città': 'Milano',
            'provincia': 'MI',
            'partita_iva': '12345678901',
            'codice_fiscale': 'RSSMRA80A01F205Z',
            'telefono': '02-1234567',
            'email': 'mario@test.com',
            'zona': 'Nord',
            'percentuale_sulle_vendite': 5.0,
            'attivo': True
        }
        
        form = RappresentanteForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_rappresentante_form_invalid_piva(self):
        """Test form rappresentante con P.IVA non valida"""
        form_data = {
            'nome': 'Mario Rossi',
            'ragione_sociale': 'Test SRL',
            'partita_iva': '123',  # P.IVA non valida
            'codice_fiscale': 'RSSMRA80A01F205Z',
            'telefono': '02-1234567',
            'email': 'mario@test.com',
            'percentuale_sulle_vendite': 5.0
        }
        
        form = RappresentanteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('partita_iva', form.errors)
    
    def test_cliente_form_clean_validation(self):
        """Test validazione personalizzata form cliente"""
        # Test senza P.IVA e CF
        form_data = {
            'ragione_sociale': 'Test Cliente',
            'telefono': '123456789',
            'email': 'cliente@test.com'
            # Mancano partita_iva e codice_fiscale
        }
        
        form = ClienteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)


class AnagraficaViewTests(TestCase):
    """Test per le views dell'anagrafica"""
    
    def setUp(self):
        """Setup per ogni test"""
        self.client = Client()
        
        # Crea utenti di test
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@test.com',
            password='testpass123',
            is_staff=True
        )
        
        self.normal_user = User.objects.create_user(
            username='normal',
            email='normal@test.com',
            password='testpass123',
            livello=Dipendente.Autorizzazioni.rappresentante
        )
        
        # Crea rappresentante per il normal_user
        self.rappresentante = Rappresentante.objects.create(
            user=self.normal_user,
            nome='Test Rappresentante',
            ragione_sociale='Test SRL',
            partita_iva='12345678901',
            codice_fiscale='12345678901',
            telefono='123456789',
            email='repr@test.com',
            percentuale_sulle_vendite=5.0
        )
        
        # Crea cliente di test
        self.cliente = Cliente.objects.create(
            rappresentante=self.rappresentante,
            ragione_sociale='Cliente Test',
            codice_fiscale='CLNTEST80A01F205Z',
            telefono='123456789',
            email='cliente@test.com'
        )
    
    def test_dashboard_access(self):
        """Test accesso alla dashboard"""
        # Test senza login
        response = self.client.get(reverse('anagrafica:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect al login
        
        # Test con login
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(reverse('anagrafica:dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_rappresentante_list_staff(self):
        """Test lista rappresentanti per staff"""
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(reverse('anagrafica:elenco_rappresentanti'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.rappresentante.nome)
    
    def test_rappresentante_list_non_staff(self):
        """Test lista rappresentanti per non-staff (deve essere negato)"""
        self.client.login(username='normal', password='testpass123')
        response = self.client.get(reverse('anagrafica:elenco_rappresentanti'))
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_cliente_list_rappresentante(self):
        """Test lista clienti per rappresentante"""
        self.client.login(username='normal', password='testpass123')
        response = self.client.get(reverse('anagrafica:elenco_clienti'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.cliente.ragione_sociale)
    
    def test_cliente_create_staff(self):
        """Test creazione cliente da staff"""
        self.client.login(username='staff', password='testpass123')
        
        form_data = {
            'ragione_sociale': 'Nuovo Cliente',
            'codice_fiscale': '12345678901',
            'telefono': '123456789',
            'email': 'nuovo@test.com',
            'pagamento': '01'
        }
        
        response = self.client.post(reverse('anagrafica:nuovo_cliente'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect dopo creazione
        self.assertTrue(Cliente.objects.filter(ragione_sociale='Nuovo Cliente').exists())
    
    def test_cliente_detail_access_control(self):
        """Test controllo accesso dettaglio cliente"""
        # Crea altro rappresentante e cliente
        altro_user = User.objects.create_user(
            username='altro', 
            password='testpass123',
            livello=Dipendente.Autorizzazioni.rappresentante
        )
        altro_repr = Rappresentante.objects.create(
            user=altro_user,
            nome='Altro',
            ragione_sociale='Altro SRL',
            partita_iva='98765432109',
            codice_fiscale='98765432109',
            telefono='987654321',
            email='altro@test.com',
            percentuale_sulle_vendite=5.0
        )
        altro_cliente = Cliente.objects.create(
            rappresentante=altro_repr,
            ragione_sociale='Cliente Altro',
            codice_fiscale='ALTRO80A01F205Z',
            telefono='987654321',
            email='altro.cliente@test.com'
        )
        
        # Il normal_user non dovrebbe vedere il cliente dell'altro rappresentante
        self.client.login(username='normal', password='testpass123')
        response = self.client.get(reverse('anagrafica:dettaglio_cliente', args=[altro_cliente.id]))
        self.assertEqual(response.status_code, 404)  # Not found per sicurezza


class AnagraficaAPITests(TestCase):
    """Test per le API dell'anagrafica"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Crea dati di test
        self.rappresentante = Rappresentante.objects.create(
            nome='Test Rappresentante',
            ragione_sociale='Test SRL',
            partita_iva='12345678901',
            codice_fiscale='12345678901',
            telefono='123456789',
            email='test@test.com',
            percentuale_sulle_vendite=5.0
        )
    
    def test_search_api(self):
        """Test API di ricerca"""
        response = self.client.get(reverse('anagrafica:api_search'), {'q': 'Test'})
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('results', data)
        self.assertTrue(len(data['results']) > 0)
    
    def test_validate_partita_iva_api(self):
        """Test API validazione partita IVA"""
        # Test P.IVA valida
        response = self.client.get(reverse('anagrafica:validate_partita_iva'), {
            'partita_iva': '12345678901',
            'tipo': 'cliente'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['valid'])  # Già esistente
        
        # Test P.IVA non valida
        response = self.client.get(reverse('anagrafica:validate_partita_iva'), {
            'partita_iva': '123',
            'tipo': 'cliente'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['valid'])
        self.assertIn('11 cifre', data['message'])


class AnagraficaManagementCommandTests(TestCase):
    """Test per i command di management"""
    
    def test_setup_anagrafica_command(self):
        """Test comando setup_anagrafica"""
        # Test senza dati di esempio
        call_command('setup_anagrafica')
        
        # Verifica creazione gruppi
        self.assertTrue(Group.objects.filter(name='Gestori Anagrafica').exists())
        self.assertTrue(Group.objects.filter(name='Rappresentanti').exists())
    
    def test_setup_with_sample_data(self):
        """Test comando con dati di esempio"""
        call_command('setup_anagrafica', '--create-sample-data')
        
        # Verifica creazione dati
        self.assertTrue(Rappresentante.objects.exists())
        self.assertTrue(Cliente.objects.exists())
        self.assertTrue(Fornitore.objects.exists())


class AnagraficaSignalTests(TestCase):
    """Test per i segnali"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            livello=Dipendente.Autorizzazioni.rappresentante
        )
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_rappresentante_creation_signal(self):
        """Test segnale creazione rappresentante"""
        # Crea admin per ricevere notifica
        admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='adminpass',
            is_staff=True
        )
        
        # Crea rappresentante
        rappresentante = Rappresentante.objects.create(
            user=self.user,
            nome='Test Signal',
            ragione_sociale='Test SRL',
            partita_iva='12345678901',
            codice_fiscale='12345678901',
            telefono='123456789',
            email='signal@test.com',
            percentuale_sulle_vendite=5.0
        )
        
        # Verifica invio email (in memoria)
        from django.core import mail
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Nuovo Rappresentante', mail.outbox[0].subject)


if __name__ == '__main__':
    unittest.main()