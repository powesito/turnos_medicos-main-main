from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('citas.api_urls')),
    path('', include('citas.urls')),
]

# Controlador de error 404 personalizado.
# Django SOLO usa este handler cuando DEBUG = False (en producción, o forzándolo
# temporalmente en local para probarlo). Con DEBUG = True, Django muestra su
# propia página de depuración con el traceback en vez de este handler.
handler404 = 'citas.views.error_404_view'
handler500 = 'citas.views.error_500_view'
