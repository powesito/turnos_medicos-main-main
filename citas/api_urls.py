from rest_framework.routers import DefaultRouter

from . import api_views

router = DefaultRouter()
router.register('especialidades', api_views.EspecialidadViewSet, basename='especialidad')
router.register('medicos', api_views.MedicoViewSet, basename='medico')
router.register('pacientes', api_views.PacienteViewSet, basename='paciente')
router.register('turnos', api_views.TurnoViewSet, basename='turno')
router.register('historial', api_views.HistorialTurnoViewSet, basename='historial')

urlpatterns = router.urls
