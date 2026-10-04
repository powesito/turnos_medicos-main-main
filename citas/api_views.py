from rest_framework import viewsets

from .models import Especialidad, HistorialTurno, Medico, Paciente, Turno
from .serializers import (
    EspecialidadSerializer,
    HistorialTurnoSerializer,
    MedicoSerializer,
    PacienteSerializer,
    TurnoSerializer,
)


class EspecialidadViewSet(viewsets.ModelViewSet):
    queryset = Especialidad.objects.all()
    serializer_class = EspecialidadSerializer


class MedicoViewSet(viewsets.ModelViewSet):
    queryset = Medico.objects.select_related('especialidad').all()
    serializer_class = MedicoSerializer


class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer


class TurnoViewSet(viewsets.ModelViewSet):
    queryset = Turno.objects.select_related('paciente', 'medico').all()
    serializer_class = TurnoSerializer

    def _usuario(self):
        user = self.request.user
        return user if user.is_authenticated else None

    def perform_create(self, serializer):
        turno = serializer.save()
        HistorialTurno.objects.create(
            turno=turno,
            usuario=self._usuario(),
            estado_anterior='',
            estado_nuevo=turno.estado,
            descripcion='Turno creado vía API.',
        )

    def perform_update(self, serializer):
        estado_anterior = serializer.instance.estado
        turno = serializer.save()
        if estado_anterior != turno.estado:
            HistorialTurno.objects.create(
                turno=turno,
                usuario=self._usuario(),
                estado_anterior=estado_anterior,
                estado_nuevo=turno.estado,
                descripcion='Cambio de estado vía API.',
            )


class HistorialTurnoViewSet(viewsets.ModelViewSet):
    queryset = HistorialTurno.objects.select_related('turno').all()
    serializer_class = HistorialTurnoSerializer
