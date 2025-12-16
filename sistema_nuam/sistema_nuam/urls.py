from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- AUTENTICACIÓN ---
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # --- SISTEMA ---
    path('', views.dashboard, name='dashboard'),
    path('ingreso/', views.ingreso_manual, name='ingreso_manual'),
    
    # Rutas de Carga Masiva
    path('carga/', views.carga_masiva, name='carga_masiva'),
    path('carga/confirmar/', views.confirmar_carga_masiva, name='confirmar_carga'),
    
    # Rutas de Gestión
    path('listado/', views.listado, name='listado'),
    path('eliminar/<int:id>/', views.eliminar_registro, name='eliminar_registro'),
    path('editar/<int:id>/', views.editar_registro, name='editar_registro'),
]