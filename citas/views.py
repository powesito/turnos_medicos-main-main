import datetime

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView
)

from .forms import PacienteForm, TurnoEstadoForm, TurnoForm
from .models import HistorialTurno, Medico, Paciente, Turno


class HomeView(TemplateView):
    template_name = 'citas/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        hoy = datetime.date.today()

        ctx['total_medicos'] = (
            Medico.objects
            .filter(activo=True)
            .count()
        )

        ctx['total_pacientes'] = (
            Paciente.objects.count()
        )

        ctx['turnos_hoy'] = (
            Turno.objects
            .filter(fecha=hoy)
            .exclude(
                estado=Turno.Estado.CANCELADO
            )
            .count()
        )

        ctx['proximos_turnos'] = (
            Turno.objects
            .select_related(
                'paciente',
                'medico'
            )
            .filter(fecha__gte=hoy)
            .exclude(
                estado=Turno.Estado.CANCELADO
            )
            .order_by(
                'fecha',
                'hora'
            )[:5]
        )

        return ctx


class MedicoListView(ListView):
    model = Medico
    template_name = 'citas/medico_list.html'
    context_object_name = 'medicos'

    def get_queryset(self):
        qs = (
            Medico.objects
            .filter(activo=True)
            .select_related('especialidad')
        )

        especialidad_id = self.request.GET.get(
            'especialidad'
        )

        if especialidad_id:
            qs = qs.filter(
                especialidad_id=especialidad_id
            )

        return qs

    def get_context_data(self, **kwargs):
        from .models import Especialidad

        ctx = super().get_context_data(**kwargs)

        ctx['especialidades'] = (
            Especialidad.objects.all()
        )

        ctx['especialidad_seleccionada'] = (
            self.request.GET.get(
                'especialidad',
                ''
            )
        )

        return ctx


class TurnoListView(ListView):
    model = Turno
    template_name = 'citas/turno_list.html'
    context_object_name = 'turnos'
    paginate_by = 15

    def get_queryset(self):
        qs = (
            Turno.objects
            .select_related(
                'paciente',
                'medico',
                'medico__especialidad'
            )
            .order_by(
                'fecha',
                'hora'
            )
        )

        estado = self.request.GET.get('estado')
        medico_id = self.request.GET.get('medico')
        fecha = self.request.GET.get('fecha')

        if estado:
            qs = qs.filter(
                estado=estado
            )

        if medico_id:
            qs = qs.filter(
                medico_id=medico_id
            )

        if fecha:
            qs = qs.filter(
                fecha=fecha
            )

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['medicos'] = (
            Medico.objects
            .filter(activo=True)
        )

        ctx['estados'] = (
            Turno.Estado.choices
        )

        ctx['filtros'] = (
            self.request.GET
        )

        return ctx


class TurnoDetailView(DetailView):
    model = Turno
    template_name = 'citas/turno_detail.html'
    context_object_name = 'turno'


class TurnoCreateView(CreateView):
    model = Turno
    form_class = TurnoForm
    template_name = 'citas/turno_form.html'
    success_url = reverse_lazy(
        'citas:turno_list'
    )

    def form_valid(self, form):
        turno = form.save(
            commit=False
        )

        try:
            turno.full_clean()

        except ValidationError as e:

            for field, errs in e.message_dict.items():

                for err in errs:
                    form.add_error(
                        field
                        if field in form.fields
                        else None,
                        err
                    )

            return self.form_invalid(form)

        with transaction.atomic():

            turno.save()

            # Registrar creación del turno
            HistorialTurno.objects.create(
                turno=turno,
                usuario=(
                    self.request.user
                    if self.request.user.is_authenticated
                    else None
                ),
                estado_anterior='',
                estado_nuevo=turno.estado,
                descripcion='Turno creado.'
            )

        messages.success(
            self.request,
            'Turno agendado correctamente.'
        )

        return redirect(
            self.success_url
        )


class TurnoEstadoUpdateView(UpdateView):
    model = Turno
    form_class = TurnoEstadoForm
    template_name = 'citas/turno_estado_form.html'

    def form_valid(self, form):

        turno = self.get_object()

        estado_anterior = turno.estado

        response = super().form_valid(form)

        estado_nuevo = self.object.estado

        if estado_anterior != estado_nuevo:

            HistorialTurno.objects.create(
                turno=self.object,

                usuario=(
                    self.request.user
                    if self.request.user.is_authenticated
                    else None
                ),

                estado_anterior=estado_anterior,

                estado_nuevo=estado_nuevo,

                descripcion=(
                    f'Estado cambiado de '
                    f'{turno.get_estado_display()} '
                    f'a '
                    f'{self.object.get_estado_display()}.'
                )
            )

        messages.success(
            self.request,
            'Estado del turno actualizado correctamente.'
        )

        return response

    def get_success_url(self):

        return reverse_lazy(
            'citas:turno_detail',
            args=[self.object.pk]
        )


def turno_cancelar(request, pk):

    turno = get_object_or_404(
        Turno,
        pk=pk
    )

    if request.method == 'POST':

        estado_anterior = turno.estado

        turno.estado = (
            Turno.Estado.CANCELADO
        )

        turno.save(
            update_fields=[
                'estado',
                'actualizado_en'
            ]
        )

        HistorialTurno.objects.create(
            turno=turno,

            usuario=(
                request.user
                if request.user.is_authenticated
                else None
            ),

            estado_anterior=estado_anterior,

            estado_nuevo=(
                Turno.Estado.CANCELADO
            ),

            descripcion='Turno cancelado.'
        )

        messages.success(
            request,
            'El turno fue cancelado correctamente.'
        )

        return redirect(
            'citas:turno_list'
        )

    return render(
        request,
        'citas/turno_confirm_cancel.html',
        {
            'turno': turno
        }
    )


class PacienteCreateView(CreateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'citas/paciente_form.html'
    success_url = reverse_lazy(
        'citas:turno_create'
    )

    def form_valid(self, form):

        messages.success(
            self.request,
            'Paciente registrado correctamente.'
        )

        return super().form_valid(form)


def horarios_disponibles(request):
    """
    Devuelve en JSON los horarios libres
    de un médico para una fecha dada.
    """

    medico_id = request.GET.get(
        'medico'
    )

    fecha_str = request.GET.get(
        'fecha'
    )

    if not medico_id or not fecha_str:

        return JsonResponse(
            {
                'error': (
                    'Parámetros medico y fecha '
                    'son requeridos.'
                )
            },
            status=400
        )

    medico = get_object_or_404(
        Medico,
        pk=medico_id,
        activo=True
    )

    try:

        fecha = datetime.datetime.strptime(
            fecha_str,
            '%Y-%m-%d'
        ).date()

    except ValueError:

        return JsonResponse(
            {
                'error': (
                    'Formato de fecha inválido, '
                    'use AAAA-MM-DD.'
                )
            },
            status=400
        )

    ocupados = set(
        Turno.objects
        .filter(
            medico=medico,
            fecha=fecha
        )
        .exclude(
            estado=Turno.Estado.CANCELADO
        )
        .values_list(
            'hora',
            flat=True
        )
    )

    horarios = []

    actual = datetime.datetime.combine(
        fecha,
        medico.hora_inicio_jornada
    )

    fin = datetime.datetime.combine(
        fecha,
        medico.hora_fin_jornada
    )

    paso = datetime.timedelta(
        minutes=medico.duracion_turno_min
    )

    while actual < fin:

        hora_actual = actual.time()

        if hora_actual not in ocupados:

            horarios.append(
                hora_actual.strftime('%H:%M')
            )

        actual += paso

    return JsonResponse(
        {
            'medico': medico.nombre_completo,
            'fecha': fecha_str,
            'horarios': horarios
        }
    )


def error_404_view(
    request,
    exception=None
):
    return render(
        request,
        'citas/404.html',
        status=404
    )


def error_500_view(request):

    return render(
        request,
        'citas/500.html',
        status=500
    )