from django.db import models
from django.contrib.auth.models import User

# tabla usuarios
class PerfilUsuario(models.Model):
    ROLES_SISTEMA = [
        ('JEFE', 'Jefe de Proyecto'),
        ('LIDER', 'Líder de Cuadrilla'),
        ('TRABAJADOR', 'Trabajador'),
    ]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol_sistema = models.CharField(max_length=20, choices=ROLES_SISTEMA)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.get_rol_sistema_display()}"

# tabla trabajadores
class Trabajador(models.Model):
    DISPONIBILIDAD = [
        ('DISPONIBLE', 'Disponible'),
        ('ASIGNADO', 'Asignado'),
        ('NO_DISPONIBLE', 'No Disponible')
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    
    primer_nombre = models.CharField(max_length=50)
    segundo_nombre = models.CharField(max_length=50, blank=True, null=True)
    apellido_paterno = models.CharField(max_length=50)
    apellido_materno = models.CharField(max_length=50)
    especialidad = models.CharField(max_length=100)
    disponibilidad = models.CharField(max_length=20, choices=DISPONIBILIDAD, default='DISPONIBLE')
		
    @property
    def nombre_completo(self):
        nombres = [self.primer_nombre, self.segundo_nombre, self.apellido_paterno, self.apellido_materno]
        return " ".join(filter(None, nombres))

    def __str__(self):
        return self.nombre_completo

# tabla roles
class Rol(models.Model):
    nombre_rol = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_rol

# tabla proyectos
class Proyecto(models.Model):
    ESTADOS = [
        ('PLANIFICADO', 'Planificado'),
        ('EN_CURSO', 'En Curso'),
        ('FINALIZADO', 'Finalizado'),
    ]

    nombre = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PLANIFICADO')
    fecha_inicio = models.DateField()
    fecha_termino = models.DateField(null=True, blank=True)
    
    jefe_proyecto = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='proyectos_a_cargo')

    def __str__(self):
        return self.nombre

# tabla cuadrillas
class Cuadrilla(models.Model):
    nombre = models.CharField(max_length=100)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='cuadrillas')
    
    miembros = models.ManyToManyField(Trabajador, through='MiembroCuadrilla')

    def __str__(self):
        return f"{self.nombre} ({self.proyecto.nombre})"

# tabla cuadrilla_miembros
class MiembroCuadrilla(models.Model):
    cuadrilla = models.ForeignKey(Cuadrilla, on_delete=models.CASCADE)
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE)
    
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True)
    fecha_asignacion = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('cuadrilla', 'trabajador')