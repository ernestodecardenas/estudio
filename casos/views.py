from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import Cliente, Caso, EstadoCaso, Pago, Expediente

# --- MANTENEDOR CLIENTES ---
def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'casos/lista_clientes.html', {'clientes': clientes})

def crear_cliente(request):
    if request.method == 'POST':
        Cliente.objects.create(
            nombres=request.POST['nombres'],
            documento=request.POST['documento'],
            telefono=request.POST['telefono'],
            correo=request.POST['correo']
        )
        return redirect('lista_clientes')
    return render(request, 'casos/form_cliente.html', {'titulo': 'Nuevo Cliente'})

def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.nombres = request.POST['nombres']
        cliente.documento = request.POST['documento']
        cliente.telefono = request.POST['telefono']
        cliente.correo = request.POST['correo']
        cliente.save()
        return redirect('lista_clientes')
    return render(request, 'casos/form_cliente.html', {'cliente': cliente, 'titulo': 'Editar Cliente'})

def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        return redirect('lista_clientes')
    return render(request, 'casos/confirmar_eliminar.html', {'cliente': cliente})

# --- CASOS Y COOKIES ---
def lista_casos(request):
    estado_id = request.GET.get('estado')
    
    if not estado_id:
        estado_id = request.COOKIES.get('ultimo_estado')

    casos = Caso.objects.all()
    if estado_id:
        casos = casos.filter(estado_id=estado_id)

    estados = EstadoCaso.objects.all()
    
    response = render(request, 'casos/lista_casos.html', {
        'casos': casos,
        'estados': estados,
        'estado_seleccionado': str(estado_id) if estado_id else ''
    })

    if request.GET.get('estado'):
        response.set_cookie('ultimo_estado', request.GET.get('estado'), max_age=3600*24)

    return response

def detalle_caso(request, pk):
    caso = get_object_or_404(Caso, pk=pk)
    
    if request.method == 'POST':
        monto = request.POST.get('monto')
        descripcion = request.POST.get('descripcion')
        
        try:
            pago = Pago(caso=caso, monto=monto, descripcion=descripcion)
            pago.full_clean()
            pago.save()
            messages.success(request, f"Pago de S/. {float(monto):.2f} registrado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al registrar pago: {e}")
            
        return redirect('detalle_caso', pk=caso.pk)

    return render(request, 'casos/detalle_caso.html', {'caso': caso})

def subir_documento(request, pk):
    caso = get_object_or_404(Caso, pk=pk)
    if request.method == 'POST' and request.FILES.get('documento'):
        expediente_id = request.POST.get('expediente_id')
        expediente = get_object_or_404(Expediente, pk=expediente_id, caso=caso)
        expediente.documento = request.FILES['documento']
        expediente.save()
        messages.success(request, "Documento subido con éxito.")
    return redirect('detalle_caso', pk=caso.pk)

# --- API JSON ---
def api_caso(request, pk):
    caso = get_object_or_404(Caso, pk=pk)
    data = {
        'codigo': caso.codigo,
        'cliente': caso.cliente.nombres,
        'estado': caso.estado.nombre,
        'abogados': [str(a) for a in caso.abogados.all()],
        'num_expedientes': caso.expedientes.count(),
        'total_pagado': float(caso.total_pagado()),
    }
    return JsonResponse(data)