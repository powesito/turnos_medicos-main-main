from django import forms
from django.utils import timezone

from .models import Medico, Paciente, Turno


class TurnoForm(forms.ModelForm):

    fecha = forms.DateField(
        label='Fecha',
        input_formats=[
            '%Y-%m-%d',
            '%d/%m/%Y'
        ],
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date',
                'class': 'form-control',
            }
        )
    )

    hora = forms.TimeField(
        label='Hora',
        input_formats=['%H:%M'],
        widget=forms.TimeInput(
            format='%H:%M',
            attrs={
                'type': 'time',
                'class': 'form-control',
            }
        )
    )

    class Meta:
        model = Turno

        fields = [
            'paciente',
            'medico',
            'fecha',
            'hora',
            'motivo'
        ]

        widgets = {
            'paciente': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'medico': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'motivo': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej: Control anual'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Mostrar solamente médicos activos
        self.fields['medico'].queryset = (
            Medico.objects.filter(activo=True)
        )

        # Impedir seleccionar fechas anteriores a hoy
        self.fields['fecha'].widget.attrs['min'] = (
            timezone.localdate().strftime('%Y-%m-%d')
        )


class PacienteForm(forms.ModelForm):

    class Meta:
        model = Paciente

        fields = [
            'nombre_completo',
            'rut_o_documento',
            'email',
            'telefono',
            'fecha_nacimiento'
        ]

        widgets = {
            'nombre_completo': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'rut_o_documento': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'telefono': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'fecha_nacimiento': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
        }


class TurnoEstadoForm(forms.ModelForm):

    class Meta:
        model = Turno

        fields = [
            'estado',
            'notas'
        ]

        widgets = {
            'estado': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'notas': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Ingrese notas del turno...'
                }
            ),
        }