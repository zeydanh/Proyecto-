from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required # Importante
from .models import CalificacionTributaria
from django.db.models import Q
import csv
import io
from datetime import datetime

# 1. DASHBOARD
@login_required
def dashboard(request):
    total = CalificacionTributaria.objects.count()
    ultimos = CalificacionTributaria.objects.order_by('-fecha_creacion')[:5]
    return render(request, 'dashboard.html', {'total': total, 'ultimos': ultimos})

# 2. INGRESO MANUAL
@login_required
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

            for i in range(8, 38):
                val = request.POST.get(f'factor_{i}')
                datos[f'factor_{i}'] = val if val else 0.0

            CalificacionTributaria.objects.create(**datos)
            
            messages.success(request, '✅ Registro guardado exitosamente.')
            return redirect('ingreso_manual')
            
        except Exception as e:
            messages.error(request, f'❌ Error al guardar: {str(e)}')

    return render(request, 'ingreso_manual.html')

# 3. CARGA MASIVA (ETAPA 1: VALIDACIÓN)
@login_required
def carga_masiva(request):
    if request.method == 'POST' and request.FILES.get('archivo_csv'):
        archivo = request.FILES['archivo_csv']
        try:
            decoded_file = archivo.read().decode('utf-8-sig')
            io_string = io.StringIO(decoded_file)
            csv_reader = csv.reader(io_string, delimiter=',')
            next(csv_reader, None) # Saltar encabezado

            validos = []
            errores = []
            
            for row_idx, row in enumerate(csv_reader, start=1):
                if len(row) >= 38: 
                    try:
                        fecha_str = row[3].strip()
                        fecha_fmt = ""
                        try:
                            fecha_obj = datetime.strptime(fecha_str, '%d-%m-%Y')
                            fecha_fmt = fecha_obj.strftime('%Y-%m-%d')
                        except ValueError:
                            try:
                                fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
                                fecha_fmt = fecha_obj.strftime('%Y-%m-%d')
                            except ValueError:
                                raise ValueError(f"Formato de fecha inválido: '{fecha_str}'")

                        item = {
                            'rut_cliente': "GENERICO_MASIVO",
                            'razon_social': row[2].strip(),
                            'ejercicio': int(row[0].strip()),
                            'mercado': row[1].strip(),
                            'instrumento': row[2].strip(),
                            'fecha_pago': fecha_fmt,
                            'secuencia': int(row[4].strip()),
                            'numero_dividendo': int(row[5].strip()),
                            'tipo_sociedad': row[6].strip(),
                            'valor_historico': float(row[7].strip() or 0),
                            'descripcion': "Carga Masiva CSV",
                            'factor_actualizacion': 0.0,
                            'origen': "ARCHIVO CSV",
                        }
                        
                        for i in range(8, 38):
                            val_str = row[i].strip() if i < len(row) else 0
                            val_float = float(val_str) if val_str else 0.0
                            item[f'factor_{i}'] = val_float

                        validos.append(item)

                    except Exception as e:
                        errores.append({
                            'fila': row_idx + 1,
                            'error': str(e),
                            'datos': f"{row[0]} - {row[2]}" if len(row) > 2 else "Fila vacía"
                        })
                else:
                    errores.append({
                        'fila': row_idx + 1,
                        'error': f"Faltan columnas. Se encontraron {len(row)}.",
                        'datos': str(row[:3])
                    })
            
            request.session['carga_validos'] = validos
            request.session['carga_errores'] = errores
            return redirect('confirmar_carga')

        except Exception as e:
            messages.error(request, f'❌ Error crítico al leer el archivo: {str(e)}')

    return render(request, 'carga_masiva.html')

# 3.1. CONFIRMACIÓN (ETAPA 2)
@login_required
def confirmar_carga_masiva(request):
    validos = request.session.get('carga_validos', [])
    errores = request.session.get('carga_errores', [])

    if request.method == 'POST':
        if not validos:
            messages.warning(request, "No hay registros válidos para insertar.")
            return redirect('carga_masiva')
            
        try:
            objs = []
            for item in validos:
                fecha_obj = datetime.strptime(item['fecha_pago'], '%Y-%m-%d').date()
                item['fecha_pago'] = fecha_obj
                objs.append(CalificacionTributaria(**item))
            
            CalificacionTributaria.objects.bulk_create(objs)
            
            if 'carga_validos' in request.session: del request.session['carga_validos']
            if 'carga_errores' in request.session: del request.session['carga_errores']
            
            messages.success(request, f'✅ Se insertaron correctamente {len(objs)} registros.')
            return redirect('listado')
            
        except Exception as e:
            messages.error(request, f'❌ Error final al guardar: {str(e)}')

    return render(request, 'confirmar_carga.html', {
        'validos': validos,
        'errores': errores,
        'total_validos': len(validos),
        'total_errores': len(errores)
    })

# 4. LISTADO
@login_required
def listado(request):
    registros = CalificacionTributaria.objects.all().order_by('-fecha_creacion')
    
    year = request.GET.get('year')
    if year: registros = registros.filter(ejercicio=year)
    
    q = request.GET.get('q')
    if q:
        registros = registros.filter(
            Q(rut_cliente__icontains=q) |
            Q(instrumento__icontains=q) |
            Q(mercado__icontains=q) |
            Q(descripcion__icontains=q)
        )

    anios_disponibles = CalificacionTributaria.objects.values_list('ejercicio', flat=True).distinct().order_by('-ejercicio')

    return render(request, 'listado.html', {
        'registros': registros,
        'anios_disponibles': anios_disponibles,
    })

# 5. ELIMINAR
@login_required
def eliminar_registro(request, id):
    registro = get_object_or_404(CalificacionTributaria, id=id)
    registro.delete()
    messages.success(request, '🗑️ Registro eliminado correctamente.')
    return redirect('listado')

# 6. EDITAR
@login_required
def editar_registro(request, id):
    registro = get_object_or_404(CalificacionTributaria, id=id)

    if request.method == 'POST':
        try:
            registro.rut_cliente = request.POST.get('rut')
            registro.razon_social = request.POST.get('razon_social')
            registro.ejercicio = request.POST.get('ejercicio')
            registro.mercado = request.POST.get('mercado')
            registro.instrumento = request.POST.get('instrumento')
            registro.descripcion = request.POST.get('descripcion')
            
            registro.fecha_pago = request.POST.get('fecha_pago')
            registro.secuencia = request.POST.get('secuencia') or 0
            registro.numero_dividendo = request.POST.get('numero_dividendo') or 0
            registro.tipo_sociedad = request.POST.get('tipo_sociedad')
            registro.valor_historico = request.POST.get('valor_historico') or 0.0
            registro.factor_actualizacion = request.POST.get('factor_actualizacion') or 0.0
            
            for i in range(8, 38):
                val = request.POST.get(f'factor_{i}')
                setattr(registro, f'factor_{i}', val if val else 0.0)

            registro.save()
            messages.success(request, '✏️ Registro actualizado correctamente.')
            return redirect('listado')

        except Exception as e:
            messages.error(request, f'❌ Error al actualizar: {str(e)}')

    lista_factores = []
    for i in range(8, 38):
        lista_factores.append({
            'num': i,
            'valor': getattr(registro, f'factor_{i}')
        })

    return render(request, 'editar_registro.html', {
        'r': registro,
        'lista_factores': lista_factores 
    })