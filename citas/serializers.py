from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Especialidad, HistorialTurno, Medico, Paciente, Turno


class EspecialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialidad
        fields = '__all__'


class MedicoSerializer(serializers.ModelSerializer):
    # Campo de solo lectura para mostrar el nombre de la especialidad
    especialidad_nombre = serializers.CharField(
        source='especialidad.nombre', read_only=True
    )

    class Meta:
        model = Medico
        fields = '__all__'

    def validate(self, attrs):
        inicio = attrs.get('hora_inicio_jornada', getattr(self.instance, 'hora_inicio_jornada', None))
        fin = attrs.get('hora_fin_jornada', getattr(self.instance, 'hora_fin_jornada', None))
        if inicio and fin and inicio >= fin:
            raise serializers.ValidationError(
                'La hora de inicio de jornada debe ser anterior a la hora de fin.'
            )
        return attrs


class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__'


class TurnoSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.CharField(
        source='paciente.nombre_completo', read_only=True
    )
    medico_nombre = serializers.CharField(
        source='medico.nombre_completo', read_only=True
    )

    class Meta:
        model = Turno
        fields = '__all__'
        read_only_fields = ('creado_en', 'actualizado_en')

    def validate(self, attrs):
        """Reutiliza las reglas de negocio de Turno.clean():
        fecha no pasada, horario del médico y sin doble reserva.
        En una actualización solo se valida si cambia médico, fecha u hora
        (así se puede, por ejemplo, marcar ATENDIDO un turno ya pasado)."""
        campos = ('paciente', 'medico', 'fecha', 'hora', 'estado')

        if self.instance:
            cambia_agenda = any(
                c in attrs and attrs[c] != getattr(self.instance, c)
                for c in ('medico', 'fecha', 'hora')
            )
            cambia_a_activo = (
                'estado' in attrs
                and attrs['estado'] != self.instance.estado
                and attrs['estado'] != Turno.Estado.CANCELADO
            )
            if not (cambia_agenda or cambia_a_activo):
                return attrs
            datos = {c: getattr(self.instance, c) for c in campos}
            pk = self.instance.pk
        else:
            datos = {}
            pk = None

        datos.update({c: v for c, v in attrs.items() if c in campos})
        turno = Turno(pk=pk, **datos)

        try:
            turno.clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict)
        return attrs


class HistorialTurnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialTurno
        fields = '__all__'
        read_only_fields = ('creado_en',)
