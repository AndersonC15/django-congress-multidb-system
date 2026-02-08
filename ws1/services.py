
import requests

def estudiante_existe(cedula):
    # OJO: Cambia el puerto 4000 u 8000 según donde estés corriendo tu runserver.
    # He agregado el "/" al final porque Django es estricto con eso.
    port = 4000 # O 8000, revisa tu terminal
    url = f"http://127.0.0.1:{port}/ws/estudiante/{cedula}/"
    
    try:
        r = requests.get(url, timeout=5)

        # Si el código de estado es 200, significa que la vista encontró al estudiante
        if r.status_code == 200:
            return True
            
        # Si es 404 u otro error, asumimos que no existe
        return False
        
    except requests.exceptions.RequestException as e:
        # Si no se puede conectar (servidor apagado o puerto mal), imprime el error
        print(f"Error conectando al servicio de estudiantes: {e}")
        return False