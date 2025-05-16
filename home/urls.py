# home/urls.py
from django.urls import path
from . import views, api_views

app_name = 'home'

urlpatterns = [
     path('landing/', views.landing_page, name='landing_page'),
    path('dashboard', views.index, name='index'),
    path('chat/', views.chat, name='chat'),
    path('promemoria/', views.promemoria_list, name='promemoria_list'),
    path('promemoria/nuovo/', views.promemoria_create, name='promemoria_create'),
    path('promemoria/<int:pk>/modifica/', views.promemoria_update, name='promemoria_update'),
    path('promemoria/<int:pk>/toggle/', views.promemoria_toggle, name='promemoria_toggle'),
    path('promemoria/<int:pk>/elimina/', views.promemoria_delete, name='promemoria_delete'),
     # API endpoints (opzionali)
    path('api/check-messages/', api_views.check_messages, name='api_check_messages'),
    path('api/mark-read/<int:message_id>/', api_views.mark_message_read, name='api_mark_read'),
    path('search/', views.global_search, name='global_search'),
    path('api/quick-search/', views.quick_search, name='quick_search'),
]
