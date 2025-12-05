from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth import logout
from .models import Cuadrilla, Proyecto, Trabajador, MiembroCuadrilla, Rol

@login_required
def dashboard(request):
    usuario = request.user

    if usuario.is_superuser:
        cuadrillas = Cuadrilla.objects.all()
        proyectos = Proyecto.objects.all()
    else:
        proyectos = Proyecto.objects.filter(jefe_proyecto=usuario)
        cuadrillas = Cuadrilla.objects.filter(proyecto__in=proyectos)
    
    es_jefe = usuario.is_superuser or (hasattr(usuario, 'perfil') and usuario.perfil.rol_sistema == 'JEFE')

    return render(request, 'cuadrillas/dashboard.html', {
        'cuadrillas': cuadrillas,
        'proyectos': proyectos,
        'es_jefe': es_jefe,
    })

@login_required
def crear_cuadrilla(request):
    es_jefe = request.user.is_superuser or (hasattr(request.user, 'perfil') and request.user.perfil.rol_sistema == 'JEFE')
    if not es_jefe:
        messages.error(request, "No tienes permisos para crear cuadrillas.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        nombre = request.POST['nombre']
        proyecto_id = request.POST['proyecto']

        if request.user.is_superuser:
             proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
        else:
             proyecto = get_object_or_404(Proyecto, pk=proyecto_id, jefe_proyecto=request.user)
        
        nueva_cuadrilla = Cuadrilla.objects.create(nombre=nombre, proyecto=proyecto)
        return redirect('detalle_cuadrilla', id=nueva_cuadrilla.id)
    
    return redirect('dashboard')

@login_required
def detalle_cuadrilla(request, id):
    cuadrilla = get_object_or_404(Cuadrilla, id=id)

    if not request.user.is_superuser and cuadrilla.proyecto.jefe_proyecto != request.user:
        messages.error(request, "Acceso denegado: No eres el Jefe de este proyecto.")
        return redirect('dashboard')
    
    es_jefe_o_admin = request.user.is_superuser or cuadrilla.proyecto.jefe_proyecto == request.user

    miembros = MiembroCuadrilla.objects.filter(cuadrilla=cuadrilla)
    

    trabajadores_disponibles = Trabajador.objects.filter(disponibilidad='DISPONIBLE')
    roles_disponibles = Rol.objects.all()


    todas_las_cuadrillas = Cuadrilla.objects.all()
    opciones_disponibilidad = Trabajador.DISPONIBILIDAD

    if request.method == 'POST':
        trabajador_id = request.POST.get('trabajador')
        rol_id = request.POST.get('rol')
        
        if trabajador_id and rol_id:
            trabajador = get_object_or_404(Trabajador, pk=trabajador_id)


            relaciones_antiguas = MiembroCuadrilla.objects.filter(trabajador=trabajador)
            
            if relaciones_antiguas.exists():
                if trabajador.disponibilidad == 'DISPONIBLE':
                    relaciones_antiguas.delete()
                else:
                    messages.error(request, f"Error: {trabajador.nombre_completo} ya pertenece a otro equipo.")
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
        'roles': roles_disponibles,               
        'todas_las_cuadrillas': todas_las_cuadrillas,   
        'opciones_disponibilidad': opciones_disponibilidad,
        'es_autorizado': es_jefe_o_admin,
    })

@login_required
def eliminar_miembro(request, miembro_id):
    miembro = get_object_or_404(MiembroCuadrilla, id=miembro_id)

    if not request.user.is_superuser and miembro.cuadrilla.proyecto.jefe_proyecto != request.user:
        messages.error(request, "No tienes permisos para modificar esta cuadrilla.")
        return redirect('dashboard')

    cuadrilla_id = miembro.cuadrilla.id
    
    trabajador = miembro.trabajador
    trabajador.disponibilidad = 'DISPONIBLE'
    trabajador.save()
    
    miembro.delete()
    
    messages.success(request, f"{trabajador.nombre_completo} ha sido retirado y está disponible nuevamente.")
    return redirect('detalle_cuadrilla', id=cuadrilla_id)

@login_required
def editar_miembro(request, miembro_id):
    miembro = get_object_or_404(MiembroCuadrilla, id=miembro_id)

    if not request.user.is_superuser and miembro.cuadrilla.proyecto.jefe_proyecto != request.user:
        messages.error(request, "No tienes permisos.")
        return redirect('dashboard')

    cuadrilla_actual_id = miembro.cuadrilla.id
    
    if request.method == 'POST':
        nuevo_rol_id = request.POST.get('nuevo_rol')
        nuevo_estado = request.POST.get('nuevo_estado')
        nueva_cuadrilla_id = request.POST.get('nueva_cuadrilla')

        rol_lider = Rol.objects.filter(nombre_rol__icontains='Líder').first()
        if rol_lider and miembro.rol == rol_lider:
            if int(nuevo_rol_id) != rol_lider.id or int(nueva_cuadrilla_id) != cuadrilla_actual_id:
                otros_lideres = MiembroCuadrilla.objects.filter(
                    cuadrilla_id=cuadrilla_actual_id, 
                    rol=rol_lider
                ).exclude(id=miembro_id).count()
                
                if otros_lideres == 0:
                    messages.error(request, "No se pueden guardar los cambios: La cuadrilla debe tener al menos un Líder.")
                    return redirect('detalle_cuadrilla', id=cuadrilla_actual_id)

        miembro.rol = get_object_or_404(Rol, id=nuevo_rol_id)
        
        trabajador = miembro.trabajador
        trabajador.disponibilidad = nuevo_estado
        trabajador.save()

        msg_extra = ""
        if int(nueva_cuadrilla_id) != cuadrilla_actual_id:
            nueva_cuadrilla = get_object_or_404(Cuadrilla, id=nueva_cuadrilla_id)
            miembro.cuadrilla = nueva_cuadrilla
            msg_extra = f" y movido a la cuadrilla '{nueva_cuadrilla.nombre}'"

        miembro.save()

        messages.success(request, f"Cambios guardados.{msg_extra} Los trabajadores han sido notificados.")
        
        return redirect('detalle_cuadrilla', id=cuadrilla_actual_id)

    return redirect('detalle_cuadrilla', id=cuadrilla_actual_id)

def cerrar_sesion(request):
    logout(request)
    return redirect('login')