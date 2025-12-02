from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import CalificacionTributaria
import csv
import io
from datetime import datetime

# 1. DASHBOARD
def dashboard(request):
    total = CalificacionTributaria.objects.count()
    ultimos = CalificacionTributaria.objects.order_by('-fecha_creacion')[:5]
    return render(request, 'dashboard.html', {'total': total, 'ultimos': ultimos})

# 2. INGRESO MANUAL COMPLETO
def ingreso_manual(request):
    if request.method == 'POST':
        try:
            # Checkbox: si no está marcado, HTML no envía nada, por eso comparamos con 'on'
            es_isfut_val = request.POST.get('es_isfut') == 'on'
            
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
                
                # Campos adicionales Mockup
                'descripcion': request.POST.get('descripcion'),
                'es_isfut': es_isfut_val,
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

# 3. CARGA MASIVA (CSV)
def carga_masiva(request):
    if request.method == 'POST' and request.FILES.get('archivo_csv'):
        archivo = request.FILES['archivo_csv']
        try:
            decoded_file = archivo.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            csv_reader = csv.reader(io_string, delimiter=',')
            next(csv_reader, None) # Saltar encabezado

            count = 0
            errores = 0
            
            for row in csv_reader:
                # Validamos que tenga al menos las columnas básicas (30 factores + datos generales)
                if len(row) >= 30: 
                    try:
                        fecha_str = row[3].strip() 
                        fecha_obj = datetime.strptime(fecha_str, '%d-%m-%Y').date()

                        datos_csv = {
                            'rut_cliente': "GENERICO_MASIVO",
                            'razon_social': row[2].strip(),
                            'ejercicio': int(row[0].strip()),
                            'mercado': row[1].strip(),
                            'instrumento': row[2].strip(),
                            'fecha_pago': fecha_obj,
                            'secuencia': int(row[4].strip()),
                            'numero_dividendo': int(row[5].strip()),
                            'tipo_sociedad': row[6].strip(),
                            'valor_historico': float(row[7].strip() or 0),
                            
                            # Defaults para campos nuevos no presentes en CSV 3.1
                            'descripcion': "Carga Masiva CSV",
                            'es_isfut': False,
                            'factor_actualizacion': 0.0,
                            'origen': "ARCHIVO CSV",
                        }
                        
                        # Mapeo de Factores dinámico del índice 8 en adelante
                        for i in range(8, 38):
                            # El índice en CSV es row[8] para factor_8, row[9] para factor_9...
                            # Como el rango es exacto, podemos usar 'i' directamente
                            val = row[i].strip() if i < len(row) else 0
                            datos_csv[f'factor_{i}'] = float(val or 0)

                        CalificacionTributaria.objects.create(**datos_csv)
                        count += 1
                    except Exception as e:
                        errores += 1
                        continue
            
            if count > 0:
                messages.success(request, f'📂 Carga finalizada: {count} registros importados.')
            if errores > 0:
                messages.warning(request, f'⚠️ {errores} registros fallaron.')
                
            return redirect('carga_masiva')

        except Exception as e:
            messages.error(request, '❌ Error crítico al leer el archivo.')

    return render(request, 'carga_masiva.html')

# 4. LISTADO y ELIMINAR
def listado(request):
    registros = CalificacionTributaria.objects.all().order_by('-fecha_creacion')
    return render(request, 'listado.html', {'registros': registros})

def eliminar_registro(request, id):
    registro = get_object_or_404(CalificacionTributaria, id=id)
    registro.delete()
    messages.success(request, '🗑️ Registro eliminado correctamente.')
    return redirect('listado')