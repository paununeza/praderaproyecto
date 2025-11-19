from django.contrib import admin
from .models import Trabajador, Proyecto, Cuadrilla, MiembroCuadrilla, Rol, PerfilUsuario

class TrabajadorAdmin(admin.ModelAdmin):
    list_display = ('primer_nombre', 'apellido_paterno', 'apellido_materno', 'especialidad', 'disponibilidad')
    search_fields = ('primer_nombre', 'apellido_paterno', 'apellido_materno', 'usuario__username')
    list_filter = ('disponibilidad', 'especialidad')

class MiembroInline(admin.TabularInline):
    model = MiembroCuadrilla
    extra = 1
    autocomplete_fields = ['trabajador']

class CuadrillaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'proyecto', 'get_miembros_count')
    list_filter = ('proyecto',)
    inlines = [MiembroInline]

    def get_miembros_count(self, obj):
        return obj.miembros.count()
    get_miembros_count.short_description = 'N° Miembros'

class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'estado', 'fecha_inicio', 'jefe_proyecto')
    list_filter = ('estado',)


admin.site.register(Trabajador, TrabajadorAdmin)
admin.site.register(Cuadrilla, CuadrillaAdmin)
admin.site.register(Proyecto, ProyectoAdmin)
admin.site.register(Rol)
admin.site.register(PerfilUsuario)