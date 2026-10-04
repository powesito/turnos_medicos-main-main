from django.contrib import admin

from .models import (
    Especialidad,
    HistorialTurno,
    Medico,
    Paciente,
    Turno,
)


@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'descripcion',
    )

    search_fields = (
        'nombre',
    )


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre_completo',
        'especialidad',
        'email',
        'telefono',
        'activo',
    )

    list_filter = (
        'especialidad',
        'activo',
    )

    search_fields = (
        'nombre_completo',
        'email',
    )


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = (
        'nombre_completo',
        'rut_o_documento',
        'email',
        'telefono',
    )

    search_fields = (
        'nombre_completo',
        'rut_o_documento',
        'email',
    )


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'fecha',
        'hora',
        'paciente',
        'medico',
        'estado',
    )

    list_filter = (
        'estado',
        'medico',
        'fecha',
    )

    search_fields = (
        'paciente__nombre_completo',
        'paciente__rut_o_documento',
        'medico__nombre_completo',
    )

    ordering = (
        'fecha',
        'hora',
    )


@admin.register(HistorialTurno)
class HistorialTurnoAdmin(admin.ModelAdmin):
    list_display = (
        'turno',
        'usuario',
        'estado_anterior',
        'estado_nuevo',
        'descripcion',
        'creado_en',
    )

    list_filter = (
        'estado_anterior',
        'estado_nuevo',
        'creado_en',
    )

    search_fields = (
        'turno__paciente__nombre_completo',
        'turno__medico__nombre_completo',
        'usuario__username',
        'descripcion',
    )

    readonly_fields = (
        'turno',
        'usuario',
        'estado_anterior',
        'estado_nuevo',
        'descripcion',
        'creado_en',
    )

    ordering = (
        '-creado_en',
    )