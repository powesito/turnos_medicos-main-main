import datetime

from django.core.management.base import BaseCommand

from citas.models import Especialidad, Medico, Paciente


class Command(BaseCommand):
    help = 'Carga especialidades, médicos y pacientes de ejemplo para probar el sistema.'

    def handle(self, *args, **options):
        especialidades = ['Medicina General', 'Pediatría', 'Cardiología', 'Dermatología', 'Traumatología']
        for nombre in especialidades:
            Especialidad.objects.get_or_create(nombre=nombre)
        self.stdout.write(self.style.SUCCESS(f'{len(especialidades)} especialidades listas.'))

        medicos = [
            ('Ana Torres', 'Medicina General', 30, datetime.time(9, 0), datetime.time(17, 0)),
            ('Carlos Muñoz', 'Pediatría', 20, datetime.time(8, 30), datetime.time(14, 0)),
            ('Beatriz Rojas', 'Cardiología', 40, datetime.time(10, 0), datetime.time(18, 0)),
            ('Diego Fuentes', 'Dermatología', 30, datetime.time(9, 0), datetime.time(13, 0)),
        ]
        for nombre, esp_nombre, duracion, inicio, fin in medicos:
            esp = Especialidad.objects.get(nombre=esp_nombre)
            Medico.objects.get_or_create(
                nombre_completo=nombre,
                defaults=dict(
                    especialidad=esp,
                    duracion_turno_min=duracion,
                    hora_inicio_jornada=inicio,
                    hora_fin_jornada=fin,
                ),
            )
        self.stdout.write(self.style.SUCCESS(f'{len(medicos)} médicos listos.'))

        pacientes = [
            ('Juan Pérez', '11.111.111-1'),
            ('María López', '22.222.222-2'),
            ('Pedro Sánchez', '33.333.333-3'),
        ]
        for nombre, rut in pacientes:
            Paciente.objects.get_or_create(nombre_completo=nombre, rut_o_documento=rut)
        self.stdout.write(self.style.SUCCESS(f'{len(pacientes)} pacientes listos.'))

        self.stdout.write(self.style.SUCCESS('Datos de ejemplo cargados correctamente.'))
