# anagrafica/management/commands/setup_anagrafica.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from anagrafica.models import Rappresentante, Cliente, Fornitore


class Command(BaseCommand):
    help = 'Configura i dati iniziali per l\'app anagrafica'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-sample-data',
            action='store_true',
            help='Crea dati di esempio',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Configurazione app anagrafica in corso...'))
        
        # 1. Creazione gruppi di permessi
        self.create_permission_groups()
        
        # 2. Creazione dati di esempio (se richiesto)
        if options['create_sample_data']:
            self.create_sample_data()
        
        self.stdout.write(self.style.SUCCESS('Configurazione completata!'))
    
    def create_permission_groups(self):
        """Crea i gruppi di permessi per l'anagrafica"""
        self.stdout.write('Creazione gruppi di permessi...')
        
        # Gruppo Gestori Anagrafica
        gestori_group, created = Group.objects.get_or_create(name='Gestori Anagrafica')
        if created:
            # Permessi per rappresentanti
            content_type_repr = ContentType.objects.get_for_model(Rappresentante)
            repr_permissions = Permission.objects.filter(content_type=content_type_repr)
            gestori_group.permissions.add(*repr_permissions)
            
            # Permessi per clienti
            content_type_cliente = ContentType.objects.get_for_model(Cliente)
            cliente_permissions = Permission.objects.filter(content_type=content_type_cliente)
            gestori_group.permissions.add(*cliente_permissions)
            
            # Permessi per fornitori
            content_type_fornitore = ContentType.objects.get_for_model(Fornitore)
            fornitore_permissions = Permission.objects.filter(content_type=content_type_fornitore)
            gestori_group.permissions.add(*fornitore_permissions)
            
            self.stdout.write(f'✓ Gruppo "{gestori_group.name}" creato')
        else:
            self.stdout.write(f'✓ Gruppo "{gestori_group.name}" già esistente')
        
        # Gruppo Rappresentanti
        rappresentanti_group, created = Group.objects.get_or_create(name='Rappresentanti')
        if created:
            # Solo permessi di visualizzazione e modifica per i propri clienti
            content_type_cliente = ContentType.objects.get_for_model(Cliente)
            client_perms = ['view_cliente', 'add_cliente', 'change_cliente']
            for perm_name in client_perms:
                try:
                    permission = Permission.objects.get(
                        codename=perm_name,
                        content_type=content_type_cliente
                    )
                    rappresentanti_group.permissions.add(permission)
                except Permission.DoesNotExist:
                    pass
            
            self.stdout.write(f'✓ Gruppo "{rappresentanti_group.name}" creato')
        else:
            self.stdout.write(f'✓ Gruppo "{rappresentanti_group.name}" già esistente')
    
    def create_sample_data(self):
        """Crea dati di esempio per test"""
        self.stdout.write('Creazione dati di esempio...')
        
        # Rappresentanti di esempio
        if not Rappresentante.objects.exists():
            rappresentanti_data = [
                {
                    'nome': 'Mario Rossi',
                    'ragione_sociale': 'Rossi Rappresentanze SRL',
                    'indirizzo': 'Via Roma 123',
                    'cap': '20100',
                    'città': 'Milano',
                    'provincia': 'MI',
                    'partita_iva': '12345678901',
                    'codice_fiscale': 'RSSMRA80A01F205Z',
                    'telefono': '02-1234567',
                    'email': 'mario.rossi@email.com',
                    'zona': 'Nord Italia',
                    'percentuale_sulle_vendite': 5.0,
                },
                {
                    'nome': 'Luigi Verdi',
                    'ragione_sociale': 'Verdi Commercio SNC',
                    'indirizzo': 'Via Napoli 456',
                    'cap': '00100',
                    'città': 'Roma',
                    'provincia': 'RM',
                    'partita_iva': '09876543210',
                    'codice_fiscale': 'VRDLGU75B15H501A',
                    'telefono': '06-9876543',
                    'email': 'luigi.verdi@email.com',
                    'zona': 'Centro Italia',
                    'percentuale_sulle_vendite': 4.5,
                }
            ]
            
            for data in rappresentanti_data:
                rappresentante = Rappresentante.objects.create(**data)
                self.stdout.write(f'✓ Rappresentante "{rappresentante.nome}" creato')
        
        # Clienti di esempio
        if not Cliente.objects.exists():
            rappresentante = Rappresentante.objects.first()
            clienti_data = [
                {
                    'rappresentante': rappresentante,
                    'ragione_sociale': 'ABC Srl',
                    'indirizzo': 'Via Torino 789',
                    'cap': '20100',
                    'città': 'Milano',
                    'provincia': 'MI',
                    'partita_iva': '11111111111',
                    'codice_fiscale': '11111111111',
                    'telefono': '02-1111111',
                    'email': 'info@abc.com',
                    'pagamento': '30',
                },
                {
                    'rappresentante': rappresentante,
                    'ragione_sociale': 'XYZ SpA',
                    'indirizzo': 'Via Venezia 321',
                    'cap': '20100',
                    'città': 'Milano',
                    'provincia': 'MI',
                    'partita_iva': '22222222222',
                    'codice_fiscale': '22222222222',
                    'telefono': '02-2222222',
                    'email': 'info@xyz.com',
                    'pagamento': '60',
                    'limite_credito': 50000.00,
                }
            ]
            
            for data in clienti_data:
                cliente = Cliente.objects.create(**data)
                self.stdout.write(f'✓ Cliente "{cliente.ragione_sociale}" creato')
        
        # Fornitori di esempio
        if not Fornitore.objects.exists():
            fornitori_data = [
                {
                    'ragione_sociale': 'Forniture Industriali SPA',
                    'indirizzo': 'Via dell\'Industria 100',
                    'cap': '20100',
                    'città': 'Milano',
                    'provincia': 'MI',
                    'partita_iva': '33333333333',
                    'codice_fiscale': '33333333333',
                    'telefono': '02-3333333',
                    'email': 'ordini@forniture.com',
                    'categoria': 'Materiali Industriali',
                    'pagamento': '60',
                },
                {
                    'ragione_sociale': 'Servizi Logistici SRL',
                    'indirizzo': 'Via della Logistica 200',
                    'cap': '40100',
                    'città': 'Bologna',
                    'provincia': 'BO',
                    'partita_iva': '44444444444',
                    'codice_fiscale': '44444444444',
                    'telefono': '051-4444444',
                    'email': 'info@logistica.com',
                    'categoria': 'Servizi',
                    'pagamento': '30',
                }
            ]
            
            for data in fornitori_data:
                fornitore = Fornitore.objects.create(**data)
                self.stdout.write(f'✓ Fornitore "{fornitore.ragione_sociale}" creato')
        
        self.stdout.write(self.style.SUCCESS('Dati di esempio creati!'))


# Script per backup dell'anagrafica
class BackupCommand(BaseCommand):
    help = 'Crea backup dei dati dell\'anagrafica'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            help='File di output per il backup',
            default='anagrafica_backup.json'
        )
    
    def handle(self, *args, **options):
        import json
        from django.core import serializers
        
        output_file = options['output']
        
        # Serializza i dati
        data = {
            'rappresentanti': json.loads(serializers.serialize('json', Rappresentante.objects.all())),
            'clienti': json.loads(serializers.serialize('json', Cliente.objects.all())),
            'fornitori': json.loads(serializers.serialize('json', Fornitore.objects.all())),
        }
        
        # Salva su file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.stdout.write(
            self.style.SUCCESS(f'Backup creato con successo: {output_file}')
        )