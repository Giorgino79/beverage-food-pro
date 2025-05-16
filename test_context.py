# Crea un file test_context.py nella root del progetto
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from amm.context_processors import messages_processor
from home.models import Messaggio

User = get_user_model()

# Crea un utente di test
user = User.objects.get(username='matteo')  # Sostituisci con il tuo username

# Crea una request fake
factory = RequestFactory()
request = factory.get('/')
request.user = user

# Testa il context processor
result = messages_processor(request)
print("Risultato context processor:", result)

# Controlla se ci sono messaggi nel database
messaggi = Messaggio.objects.filter(destinatario=user)
print(f"Messaggi totali per {user.username}: {messaggi.count()}")
messaggi_non_letti = messaggi.filter(letto=False)
print(f"Messaggi non letti per {user.username}: {messaggi_non_letti.count()}")