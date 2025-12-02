from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import CalificacionTributaria
import csv
import io

# 1. VISTA DASHBOARD (Inicio)
def dashboard(request):
    """
    Muestra indicadores generales del sistema.
    """
    total = CalificacionTributaria.objects.count()
    # Traemos los últimos 5 registros para mostrar actividad reciente
    ultimos = CalificacionTributaria.objects.order_by('-fecha_creacion')[:5]
    
    return render(request, 'dashboard.html', {
        'total': total,
        'ultimos': ultimos
    })

# Abre core/views.py y busca la función ingreso_manual
# Reemplázala con esta versión actualizada:

def ingreso_manual(request):
    if request.method == 'POST':
        # Recibimos los 4 datos
        rut = request.POST.get('rut')
        razon_social = request.POST.get('razon_social') # <--- NUEVO
        anio = request.POST.get('anio')                 # <--- NUEVO
        factor = request.POST.get('factor')
        
        if rut and factor:
            CalificacionTributaria.objects.create(
                rut_cliente=rut,
                razon_social=razon_social, # Guardamos Nombre
                anio=anio,                 # Guardamos Año
                factor=factor
            )
            messages.success(request, '✅ Registro completo guardado exitosamente.')
            return redirect('ingreso_manual')
            
    return render(request, 'ingreso_manual.html')

# (Opcional) Si tu profesor te pide que la Carga Masiva también tenga estos datos,
# avísame para modificar esa función también. Por ahora actualizamos el manual.
# 3. VISTA CARGA MASIVA (HDU 2.1)
def carga_masiva(request):
    """
    Procesa un archivo CSV y guarda múltiples registros.
    Formato esperado: RUT,FACTOR (sin encabezados o saltando la primera fila si falla)
    """
    if request.method == 'POST' and request.FILES.get('archivo_csv'):
        archivo = request.FILES['archivo_csv']
        
        # Decodificamos el archivo para leerlo como texto
        try:
            decoded_file = archivo.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            csv_reader = csv.reader(io_string, delimiter=',')
            
            count = 0
            errores = 0
            
            for row in csv_reader:
                # Validamos que la fila tenga al menos 2 columnas
                if len(row) >= 2:
                    try:
                        # Intentamos guardar (El modelo encriptará el RUT)
                        CalificacionTributaria.objects.create(
                            rut_cliente=row[0].strip(), 
                            factor=row[1].strip()
                        )
                        count += 1
                    except Exception as e:
                        errores += 1
                        continue # Si una fila falla, seguimos con la siguiente
            
            if count > 0:
                messages.success(request, f'📂 Carga finalizada: {count} registros importados correctamente.')
            if errores > 0:
                messages.warning(request, f'⚠️ Algunos registros ({errores}) no se pudieron leer.')
                
            return redirect('carga_masiva')

        except Exception as e:
            messages.error(request, '❌ Error al leer el archivo. Asegúrese de que sea un CSV válido.')

    return render(request, 'carga_masiva.html')

# 4. VISTA LISTADO (Auditoría)
def listado(request):
    """
    Muestra todos los registros de la base de datos SQL.
    """
    registros = CalificacionTributaria.objects.all().order_by('-fecha_creacion')
    return render(request, 'listado.html', {'registros': registros})

# 5. VISTA ELIMINAR REGISTRO (CRUD: Delete)
def eliminar_registro(request, id):
    """
    Busca un registro por su ID y lo elimina de la base de datos.
    """
    registro = get_object_or_404(CalificacionTributaria, id=id)
    registro.delete()
    messages.success(request, '🗑️ Registro eliminado correctamente.')
    return redirect('listado')
