# inscripciones/views.py
from django.shortcuts import render
from datetime import datetime
from .mongo import eventos_col, inscripciones_col
from .services import estudiante_existe
from bson import ObjectId

def registrar_evento(request):
    eventos = list(eventos_col.find())
    
    # Convertir _id a id para que sea accesible en templates
    for evento in eventos:
        evento['id'] = str(evento['_id'])
    
    mensaje = ""

    if request.method == "POST":
        cedula = request.POST["cedula"]
        evento_id = request.POST["evento"]

        if estudiante_existe(cedula):
            inscripciones_col.insert_one({
                "evento_id": ObjectId(evento_id),
                "cedula_estudiante": cedula,
                "fecha_inscripcion": datetime.now()
            })
            mensaje = "Inscripción realizada con éxito"
        else:
            mensaje = "El estudiante NO existe en el sistema académico"
            
    return render(request, "registrar.html", {
        "eventos": eventos,
        "mensaje": mensaje
    })
