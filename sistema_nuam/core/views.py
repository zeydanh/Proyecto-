from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import CalificacionTributaria
from django.db.models import Q
import csv
import io
from datetime import datetime

# 1. DASHBOARD
def dashboard(request):
    total = CalificacionTributaria.objects.count()
    ultimos = CalificacionTributaria.objects.order_by('-fecha_creacion')[:5]
    return render(request, 'dashboard.html', {'total': total, 'ultimos': ultimos})

# 2. INGRESO MANUAL
def ingreso_manual(request):
    if request.method == 'POST':
        try:
            datos = {
                'rut_cliente': request.POST.get('rut'),
                'razon_social': request.POST.get('razon_social'),
                'ejercicio': request.POST.get('ejercicio'),
                'mercado': request.POST.get('mercado'),
                'instrumento': request.POST.get('instrumento'),
                'fecha_pago': request.POST.get('fecha_pago'),
                'secuencia': request.POST.get('secuencia'),
                'numero_dividendo': request.POST.get('numero_dividendo'),
                'tipo_sociedad': request.POST.get('tipo_sociedad'),
                'valor_historico': request.POST.get('valor_historico'),
                'descripcion': request.POST.get('descripcion'),
                'factor_actualizacion': request.POST.get('factor_actualizacion') or 0.0,
                'origen': 'MANUAL', 
            }

            # Factores 8 al 37
            for i in range(8, 38):
                val = request.POST.get(f'factor_{i}')
                datos[f'factor_{i}'] = val if val else 0.0

            CalificacionTributaria.objects.create(**datos)
            
            messages.success(request, '✅ Registro guardado exitosamente.')
            return redirect('ingreso_manual')
            
        except Exception as e:
            messages.error(request, f'❌ Error al guardar: {str(e)}')

    return render(request, 'ingreso_manual.html')

# 3. CARGA MASIVA (CORREGIDO SEGÚN EXCEL)
def carga_masiva(request):
    if request.method == 'POST' and request.FILES.get('archivo_csv'):
        archivo = request.FILES['archivo_csv']
        try:
            # decodificamos con utf-8-sig para evitar problemas con BOM de Excel
            decoded_file = archivo.read().decode('utf-8-sig')
            io_string = io.StringIO(decoded_file)
            csv_reader = csv.reader(io_string, delimiter=',')
            next(csv_reader, None) # Saltar encabezado si existe

            count = 0
            errores = 0
            
            for row_idx, row in enumerate(csv_reader, start=1):
                # El Excel define 38 columnas exactas (Indices 0 al 37)
                if len(row) >= 38: 
                    try:
                        # Columna 3 es Fecha (DD-MM-AAAA)
                        fecha_str = row[3].strip() 
                        try:
                            fecha_obj = datetime.strptime(fecha_str, '%d-%m-%Y').date()
                        except ValueError:
                            # Fallback por si acaso viene en formato YYYY-MM-DD
                            fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()

                        datos_csv = {
                            'rut_cliente': "GENERICO_MASIVO", # Dato no incluido en CSV
                            'razon_social': row[2].strip(),   # Usamos Instrumento como Razón Social
                            'ejercicio': int(row[0].strip()),
                            'mercado': row[1].strip(),
                            'instrumento': row[2].strip(),
                            'fecha_pago': fecha_obj,
                            'secuencia': int(row[4].strip()),
                            'numero_dividendo': int(row[5].strip()),
                            'tipo_sociedad': row[6].strip(),
                            'valor_historico': float(row[7].strip() or 0),
                            'descripcion': "Carga Masiva CSV",
                            'factor_actualizacion': 0.0,
                            'origen': "ARCHIVO CSV",
                        }
                        
                        # Factores del 8 al 37 (Columnas índice 8 a 37 en el CSV)
                        for i in range(8, 38):
                            val_str = row[i].strip() if i < len(row) else 0
                            val_float = float(val_str) if val_str else 0.0
                            
                            # Validación lógica opcional (descomentar si se requiere estricto <= 1)
                            # if val_float > 1.0: val_float = 1.0
                            
                            datos_csv[f'factor_{i}'] = val_float

                        CalificacionTributaria.objects.create(**datos_csv)
                        count += 1
                    except Exception as e:
                        # print(f"Error fila {row_idx}: {e}") # Para debug en consola
                        errores += 1
                        continue
                else:
                    # Fila con menos columnas de las esperadas
                    errores += 1
            
            if count > 0:
                messages.success(request, f'📂 Carga finalizada: {count} registros importados.')
            if errores > 0:
                messages.warning(request, f'⚠️ {errores} registros fallaron por formato incorrecto.')
                
            return redirect('carga_masiva')

        except Exception as e:
            messages.error(request, f'❌ Error crítico al leer el archivo: {str(e)}')

    return render(request, 'carga_masiva.html')

# 4. LISTADO CON FILTROS
def listado(request):
    registros = CalificacionTributaria.objects.all().order_by('-fecha_creacion')

    # Filtro por Año
    year = request.GET.get('year')
    if year:
        registros = registros.filter(ejercicio=year)

    # Búsqueda General
    q = request.GET.get('q')
    if q:
        registros = registros.filter(
            Q(rut_cliente__icontains=q) |
            Q(instrumento__icontains=q) |
            Q(mercado__icontains=q) |
            Q(descripcion__icontains=q)
        )

    # Obtener años disponibles
    anios_disponibles = CalificacionTributaria.objects.values_list('ejercicio', flat=True).distinct().order_by('-ejercicio')

    return render(request, 'listado.html', {
        'registros': registros,
        'anios_disponibles': anios_disponibles,
        'rango_factores': range(8, 38)  # Necesario para iterar las columnas en el HTML
    })

def eliminar_registro(request, id):
    registro = get_object_or_404(CalificacionTributaria, id=id)
    registro.delete()
    messages.success(request, '🗑️ Registro eliminado correctamente.')
    return redirect('listado')