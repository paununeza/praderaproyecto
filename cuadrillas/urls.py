from django.urls import path
from . import views
from django.shortcuts import redirect

def go_to_dashboard(request):
    return redirect('dashboard')

urlpatterns = [
    path('', go_to_dashboard, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('crear-cuadrilla/', views.crear_cuadrilla, name='crear_cuadrilla'),
    path('cuadrilla/<int:id>/', views.detalle_cuadrilla, name='detalle_cuadrilla'),
    path('miembro/eliminar/<int:miembro_id>/', views.eliminar_miembro, name='eliminar_miembro'),
]