from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('ingreso/', views.ingreso_manual, name='ingreso_manual'),
    path('carga/', views.carga_masiva, name='carga_masiva'),
    path('listado/', views.listado, name='listado'),
    
    # ESTA ES LA LÍNEA QUE TE FALTA O TIENE UN ERROR:
    path('eliminar/<int:id>/', views.eliminar_registro, name='eliminar_registro'),
]