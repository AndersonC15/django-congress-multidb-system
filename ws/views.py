from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Estudiante
from .serializers import EstudianteSerializer


@api_view(['GET'])
def obtener_estudiante(request, cedula):
    try:
        estudiante = Estudiante.objects.get(cedula=cedula)
        serializer = EstudianteSerializer(estudiante)
        return Response(serializer.data)
    except Estudiante.DoesNotExist:
        return Response(
            {"error": "Estudiante no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )