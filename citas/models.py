import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Especialidad(models.Model):
    nombre = models.CharField(
        'Nombre',
        max_length=100,
        unique=True
    )

    descripcion = models.TextField(
        'Descripción',
        blank=True
    )

    class Meta:
        verbose_name = 'Especialidad'
        verbose_name_plural = 'Especialidades'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Medico(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='medico'
    )

    nombre_completo = models.CharField(
        'Nombre completo',
        max_length=150
    )

    especialidad = models.ForeignKey(
        Especialidad,
        on_delete=models.PROTECT,
        related_name='medicos'
    )

    email = models.EmailField(
        'Correo electrónico',
        blank=True
    )

    telefono = models.CharField(
        'Teléfono',
        max_length=20,
        blank=True
    )

    duracion_turno_min = models.PositiveIntegerField(
        'Duración de cada turno (min)',
        default=30
    )

    hora_inicio_jornada = models.TimeField(
        'Inicio de jornada',
        default=datetime.time(9, 0)
    )

    hora_fin_jornada = models.TimeField(
        'Fin de jornada',
        default=datetime.time(18, 0)
    )

    activo = models.BooleanField(
        'Activo',
        default=True
    )

    class Meta:
        verbose_name = 'Médico'
        verbose_name_plural = 'Médicos'
        ordering = ['nombre_completo']

    def __str__(self):
        return f'Dr(a). {self.nombre_completo} - {self.especialidad}'


class Paciente(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='paciente'
    )

    nombre_completo = models.CharField(
        'Nombre completo',
        max_length=150
    )

    rut_o_documento = models.CharField(
        'RUT / Documento',
        max_length=20,
        unique=True
    )

    email = models.EmailField(
        'Correo electrónico',
        blank=True
    )

    telefono = models.CharField(
        'Teléfono',
        max_length=20,
        blank=True
    )

    fecha_nacimiento = models.DateField(
        'Fecha de nacimiento',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['nombre_completo']

    def __str__(self):
        return f'{self.nombre_completo} ({self.rut_o_documento})'


class Turno(models.Model):

    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        CONFIRMADO = 'CONFIRMADO', 'Confirmado'
        CANCELADO = 'CANCELADO', 'Cancelado'
        ATENDIDO = 'ATENDIDO', 'Atendido'
        NO_ASISTIO = 'NO_ASISTIO', 'No asistió'

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='turnos'
    )

    medico = models.ForeignKey(
        Medico,
        on_delete=models.CASCADE,
        related_name='turnos'
    )

    fecha = models.DateField(
        'Fecha'
    )

    hora = models.TimeField(
        'Hora'
    )

    motivo = models.CharField(
        'Motivo de consulta',
        max_length=255,
        blank=True
    )

    estado = models.CharField(
        'Estado',
        max_length=12,
        choices=Estado.choices,
        default=Estado.PENDIENTE
    )

    notas = models.TextField(
        'Notas clínicas',
        blank=True
    )

    creado_en = models.DateTimeField(
        'Creado el',
        auto_now_add=True
    )

    actualizado_en = models.DateTimeField(
        'Actualizado en',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
        ordering = ['fecha', 'hora']

    def __str__(self):
        return (
            f'{self.paciente} con {self.medico} '
            f'el {self.fecha} {self.hora}'
        )

    def clean(self):
        errors = {}

        hoy = timezone.localdate()

        # No permitir fechas anteriores a hoy
        if self.fecha and self.fecha < hoy:
            errors['fecha'] = (
                'No se pueden agendar turnos en una fecha pasada.'
            )

        # Validar horario del médico
        if self.medico_id and self.hora:
            medico = self.medico

            if not (
                medico.hora_inicio_jornada
                <= self.hora
                < medico.hora_fin_jornada
            ):
                errors['hora'] = (
                    'El médico atiende entre '
                    + medico.hora_inicio_jornada.strftime('%H:%M')
                    + ' y '
                    + medico.hora_fin_jornada.strftime('%H:%M')
                    + '.'
                )

        # No permitir dos turnos del mismo médico
        # en la misma fecha y hora
        if (
            self.medico_id
            and self.fecha
            and self.hora
            and self.estado != self.Estado.CANCELADO
        ):
            turnos_existentes = Turno.objects.filter(
                medico=self.medico,
                fecha=self.fecha,
                hora=self.hora
            ).exclude(
                estado=self.Estado.CANCELADO
            )

            if self.pk:
                turnos_existentes = turnos_existentes.exclude(
                    pk=self.pk
                )

            if turnos_existentes.exists():
                errors['hora'] = (
                    'Ese médico ya tiene un turno agendado '
                    'en ese horario.'
                )

        if errors:
            raise ValidationError(errors)

    def get_absolute_url(self):
        return reverse(
            'citas:turno_detail',
            args=[self.pk]
        )

    @property
    def esta_cancelado(self):
        return self.estado == self.Estado.CANCELADO


class HistorialTurno(models.Model):
    turno = models.ForeignKey(
        Turno,
        on_delete=models.CASCADE,
        related_name='historial'
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    estado_anterior = models.CharField(
        'Estado anterior',
        max_length=12,
        blank=True
    )

    estado_nuevo = models.CharField(
        'Estado nuevo',
        max_length=12
    )

    descripcion = models.CharField(
        'Descripción',
        max_length=255,
        blank=True
    )

    creado_en = models.DateTimeField(
        'Fecha y hora',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Historial de turno'
        verbose_name_plural = 'Historial de turnos'
        ordering = ['-creado_en']

    def __str__(self):
        return (
            f'Turno #{self.turno_id}: '
            f'{self.estado_anterior or "Creado"} → '
            f'{self.estado_nuevo}'
        )