from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from cuadrillas import views as cuadrillas_views

def root_redirect(request):
    return redirect('dashboard')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_redirect),
    path('cuadrillas/', include('cuadrillas.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='cuadrillas/login.html'), name='login'),
    path('accounts/logout/', cuadrillas_views.cerrar_sesion, name='logout'),
    path('', include('cuadrillas.urls')), 
]