from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

def root_redirect(request):
    return redirect('dashboard')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cuadrillas/', include('cuadrillas.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='cuadrillas/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('', include('cuadrillas.urls')), 
]