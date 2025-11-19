from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cuadrilla, Proyecto, Trabajador, MiembroCuadrilla, Rol

@login_required
def dashboard(request):
    cuadrillas = Cuadrilla.objects.all()
    proyectos = Proyecto.objects.all()
    
    return render(request, 'cuadrillas/dashboard.html', {
        'cuadrillas': cuadrillas,
        'proyectos': proyectos
    })

@login_required
def crear_cuadrilla(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        proyecto_id = request.POST['proyecto']
        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
        
        nueva_cuadrilla = Cuadrilla.objects.create(nombre=nombre, proyecto=proyecto)
        return redirect('detalle_cuadrilla', id=nueva_cuadrilla.id)

@login_required
def detalle_cuadrilla(request, id):
    cuadrilla = get_object_or_404(Cuadrilla, id=id)
    miembros = MiembroCuadrilla.objects.filter(cuadrilla=cuadrilla)
    
    trabajadores_disponibles = Trabajador.objects.filter(disponibilidad='DISPONIBLE')
    roles_disponibles = Rol.objects.all()

    if request.method == 'POST':
        trabajador_id = request.POST.get('trabajador')
        rol_id = request.POST.get('rol')
        
        if trabajador_id and rol_id:
            trabajador = get_object_or_404(Trabajador, pk=trabajador_id)

            if trabajador.disponibilidad != 'DISPONIBLE':
                messages.error(request, f"Error: El trabajador {trabajador.nombre_completo} ya fue asignado a otra cuadrilla recientemente.")
                return redirect('detalle_cuadrilla', id=id)
            
            if MiembroCuadrilla.objects.filter(trabajador=trabajador).exists():
                 messages.error(request, f"Error: {trabajador.nombre_completo} ya pertenece a un equipo.")
                 return redirect('detalle_cuadrilla', id=id)

            rol = get_object_or_404(Rol, pk=rol_id)
            
            MiembroCuadrilla.objects.create(
                cuadrilla=cuadrilla,
                trabajador=trabajador,
                rol=rol
            )
            trabajador.disponibilidad = 'ASIGNADO'
            trabajador.save()
            
            messages.success(request, f"{trabajador.nombre_completo} asignado correctamente.")
            
        return redirect('detalle_cuadrilla', id=id)

    return render(request, 'cuadrillas/detalle_cuadrilla.html', {
        'cuadrilla': cuadrilla,
        'miembros': miembros,
        'trabajadores': trabajadores_disponibles,
        'roles': roles_disponibles
    })

@login_required
def eliminar_miembro(request, miembro_id):
    miembro = get_object_or_404(MiembroCuadrilla, id=miembro_id)
    cuadrilla_id = miembro.cuadrilla.id

    trabajador = miembro.trabajador
    trabajador.disponibilidad = 'DISPONIBLE'
    trabajador.save()
    
    miembro.delete()
    return redirect('detalle_cuadrilla', id=cuadrilla_id)