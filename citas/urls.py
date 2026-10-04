from django.urls import path

from . import views

app_name = 'citas'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),

    path('medicos/', views.MedicoListView.as_view(), name='medico_list'),

    path('turnos/', views.TurnoListView.as_view(), name='turno_list'),
    path('turnos/nuevo/', views.TurnoCreateView.as_view(), name='turno_create'),
    path('turnos/<int:pk>/', views.TurnoDetailView.as_view(), name='turno_detail'),
    path('turnos/<int:pk>/estado/', views.TurnoEstadoUpdateView.as_view(), name='turno_estado'),
    path('turnos/<int:pk>/cancelar/', views.turno_cancelar, name='turno_cancelar'),

    path('pacientes/nuevo/', views.PacienteCreateView.as_view(), name='paciente_create'),

    path('api/horarios-disponibles/', views.horarios_disponibles, name='horarios_disponibles'),
]
