from django.db import models


class Estudiante(models.Model):
    id_estudiante = models.AutoField(primary_key=True)
    cedula = models.CharField(max_length=10)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    carrera_id = models.IntegerField()
    fecha_ingreso = models.DateField()

    class Meta:
        db_table = 'estudiantes'
        managed = False   # MUY IMPORTANTE

"""
class Calificacion(models.Model):
    id_calificacion = models.AutoField(primary_key=True)
    detalle_matricula_id = models.IntegerField()
    nota_final = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = 'calificaciones'
"""