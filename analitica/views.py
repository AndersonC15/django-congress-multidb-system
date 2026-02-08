from django.shortcuts import render
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from pymongo import MongoClient
import matplotlib

# Evitar errores de GUI en servidor
matplotlib.use('Agg') 

def dashboard_view(request):
    # --- 1. CONEXIÓN A MONGO ---
    client = MongoClient('mongodb://localhost:27017/')
    db = client['sistema_academico']
    collection = db['inscripciones_evento']
    
    data = list(collection.find())
    df = pd.DataFrame(data)
    
    # Contexto inicial vacío por si no hay datos
    context = {
        'hay_datos': False,
        'mensaje': 'No se encontraron registros en la base de datos.'
    }

    if not df.empty:
        # --- 2. LIMPIEZA Y TRANSFORMACIÓN ---
        df['fecha_inscripcion'] = pd.to_datetime(df['fecha_inscripcion'])
        df['Fecha'] = df['fecha_inscripcion'].dt.date
        df['evento_id_str'] = df['evento_id'].astype(str)

        # Mapeo Dinámico (Busca nombres reales en Mongo, fallback a manual)
        col_eventos = db['eventos']
        lista_eventos = list(col_eventos.find())
        mapa_eventos = {str(e['_id']): e['nombre'] for e in lista_eventos if 'nombre' in e}
        
        # Si Mongo no tiene los nombres, usamos tu diccionario de respaldo
        if not mapa_eventos:
            mapa_eventos = {
                "697b59db58e6c79ef92c4915": "Computación",
                "6980a0b78122aa9383d95a0b": "Minas",
                "6980bfaf8122aa9383d95a0d": "Psicología",
                "6980c0a08122aa9383d95a0e": "Telecomunicaciones",
                "6981fa33a15914560c24e565": "Finanzas"
            }
            
        df['Nombre_Evento'] = df['evento_id_str'].map(mapa_eventos).fillna(df['evento_id_str'])

        # --- 3. KPIs GENERALES ---
        total_inscritos = len(df)
        total_asistieron = df['asistio'].sum()
        tasa_global = (total_asistieron / total_inscritos) * 100 if total_inscritos > 0 else 0
        ausentismo = 100 - tasa_global

        kpis = {
            'total': total_inscritos,
            'asistieron': total_asistieron,
            'tasa': round(tasa_global, 2),
            'ausentismo': round(ausentismo, 2)
        }

        # --- 4. VISUALIZACIÓN (GENERAR IMÁGENES) ---
        plt.style.use('dark_background')
        params = {
            "axes.facecolor": "#0f172a", # Slate 900
            "figure.facecolor": "#0f172a", 
            "grid.color": "#334155",      # Slate 700
            "text.color": "white",
            "axes.labelcolor": "#22d3ee", # Cyan
            "xtick.color": "white",
            "ytick.color": "white"
        }
        plt.rcParams.update(params)

        def get_graph():
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', transparent=False)
            buffer.seek(0)
            img = base64.b64encode(buffer.getvalue()).decode('utf-8')
            buffer.close()
            plt.close()
            return img

        # GRÁFICO 1: Asistencia vs Ausencia
        plt.figure(figsize=(10, 6))
        colores = ['#ef4444', '#22c55e'] # Rojo y Verde neón
        data_grafico = df.groupby(['Nombre_Evento', 'asistio']).size().unstack(fill_value=0)
        
        ax = data_grafico.plot(kind='bar', stacked=True, color=colores, width=0.7)
        plt.title('Distribución de Asistencia', fontsize=14, color='white', pad=20)
        plt.xlabel('')
        plt.xticks(rotation=15)
        plt.legend(['Ausente', 'Asistió'], facecolor='#1e293b', edgecolor='none')
        grafica_barras = get_graph()

        # GRÁFICO 2: Tasa de Efectividad
        plt.figure(figsize=(10, 6))
        tasa_evento = df.groupby('Nombre_Evento')['asistio'].mean() * 100
        sns.barplot(x=tasa_evento.index, y=tasa_evento.values, palette="viridis")
        plt.axhline(y=tasa_global, color='#f472b6', linestyle='--', label=f'Promedio ({tasa_global:.1f}%)')
        plt.title('Tasa de Efectividad (%)', fontsize=14, color='white', pad=20)
        plt.xlabel('')
        plt.ylim(0, 110)
        plt.xticks(rotation=15)
        plt.legend(facecolor='#1e293b', edgecolor='none')
        # Etiquetas
        for i, v in enumerate(tasa_evento.values):
            plt.text(i, v + 2, f"{v:.1f}%", ha='center', color='white', fontweight='bold')
        grafica_tasa = get_graph()


        # --- 5. PREPARACIÓN DE TABLAS (Convertir a diccionarios para el HTML) ---
        
        # TABLA 1: PIVOTE DETALLADA
        pivot = df.pivot_table(index='Nombre_Evento', columns='asistio', values='cedula', aggfunc='count', fill_value=0)
        if True not in pivot.columns: pivot[True] = 0
        if False not in pivot.columns: pivot[False] = 0
        pivot = pivot.rename(columns={False: 'Ausentes', True: 'Asistentes'})
        pivot['Total'] = pivot['Ausentes'] + pivot['Asistentes']
        pivot['Porcentaje'] = (pivot['Asistentes'] / pivot['Total'] * 100).round(2)
        # Convertimos a lista de diccionarios incluyendo el índice (Nombre Evento)
        tabla_pivot = pivot.reset_index().to_dict('records')

        # TABLA 2: TOP DÍAS GENERAL
        top_general = df.groupby('Fecha').size().reset_index(name='Cantidad')
        top_general = top_general.sort_values('Cantidad', ascending=False).head(5)
        tabla_top = top_general.to_dict('records')

        # TABLA 3: MEJOR DÍA POR EVENTO
        por_evento = df.groupby(['Nombre_Evento', 'Fecha']).size().reset_index(name='Inscritos')
        por_evento = por_evento.sort_values('Inscritos', ascending=False)
        mejores_dias = por_evento.drop_duplicates(subset=['Nombre_Evento']).sort_values('Nombre_Evento')
        tabla_mejor_evento = mejores_dias.to_dict('records')

        # TABLA 4: PREFERENCIA SEMANAL
        dias_esp = {
            'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
            'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
        }
        df['Dia_Nombre'] = df['fecha_inscripcion'].dt.day_name().map(dias_esp)
        tabla_semanal = df['Dia_Nombre'].value_counts().reset_index()
        tabla_semanal.columns = ['Dia', 'Total']
        tabla_semanal = tabla_semanal.to_dict('records')

        context = {
            'hay_datos': True,
            'kpis': kpis,
            'grafica_barras': grafica_barras,
            'grafica_tasa': grafica_tasa,
            'tabla_pivot': tabla_pivot,
            'tabla_top': tabla_top,
            'tabla_mejor_evento': tabla_mejor_evento,
            'tabla_semanal': tabla_semanal
        }

    return render(request, 'dashboard.html', context)