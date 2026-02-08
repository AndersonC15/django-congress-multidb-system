from django.urls import path
from .views import obtener_estudiante

urlpatterns = [
    path('estudiante/<str:cedula>/', obtener_estudiante),
]