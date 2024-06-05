#ontologia_fuzzy.py
import numpy as np
import skfuzzy as fuzzz
from flask import Flask, request, jsonify
from skfuzzy import control as ctrl
from fuzzywuzzy import fuzz
from db import mysql

class OntologiaFuzzy:
    #def __init__(self):
    #    self.habilidades = ['arte', 'musica', 'programacion']  # Agrega más habilidades según sea necesario

    def __init__(self):
        # Definir las variables difusas
        self.habilidad_usuario = ctrl.Antecedent(np.arange(0, 101, 1), 'habilidad_usuario')
        self.habilidad_docente = ctrl.Antecedent(np.arange(0, 101, 1), 'habilidad_docente')
        self.experiencia = ctrl.Antecedent(np.arange(0, 51, 1), 'experiencia')
        self.similitud = ctrl.Consequent(np.arange(0, 101, 1), 'similitud')
        
        # Definir las funciones de membresía
        self.habilidad_usuario.automf(3)
        self.habilidad_docente.automf(3)
        self.experiencia['baja'] = fuzzz.trimf(self.experiencia.universe, [0, 0, 15])
        self.experiencia['media'] = fuzzz.trimf(self.experiencia.universe, [10, 25, 40])
        self.experiencia['alta'] = fuzzz.trimf(self.experiencia.universe, [35, 50, 50])
        self.similitud.automf(3)
        
        # Definir las reglas difusas
        rule1 = ctrl.Rule(self.habilidad_usuario['poor'] | self.habilidad_docente['poor'], self.similitud['poor'])
        rule2 = ctrl.Rule(self.habilidad_usuario['average'] & self.habilidad_docente['average'], self.similitud['average'])
        rule3 = ctrl.Rule(self.habilidad_usuario['good'] & self.habilidad_docente['good'], self.similitud['good'])
        
        # Crear el sistema de control difuso
        self.similitud_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
        self.similitud_sim = ctrl.ControlSystemSimulation(self.similitud_ctrl)

    #def calcular_similitud(self, habilidad_usuario, habilidad_docente):
    #    return fuzz.ratio(habilidad_usuario, habilidad_docente)

    def calcular_similitud(self, habilidad_usuario, habilidad_docente, experiencia_docente):
        self.similitud_sim.input['habilidad_usuario'] = habilidad_usuario
        self.similitud_sim.input['habilidad_docente'] = habilidad_docente
        self.similitud_sim.input['experiencia'] = experiencia_docente
        
        # Calcular la similitud difusa
        self.similitud_sim.compute()
        return self.similitud_sim.output['similitud']


    def obtener_docentes_similares(self, habilidad_usuario, experiencia_usuario):
        # Consulta a la base de datos para obtener docentes que coincidan con la búsqueda
        # Aquí puedes utilizar la lógica de consulta a la base de datos existente
        
        cursor = mysql.connection.cursor()
        query = """
            SELECT d.id, d.nombre, d.experiencia, GROUP_CONCAT(h.habilidad SEPARATOR ', ') AS habilidades
            FROM docentes d
            JOIN docente_habilidades dh ON d.id = dh.id_docente
            JOIN habilidades h ON dh.id_habilidad = h.id
            WHERE d.experiencia >= %s
            GROUP BY d.id
        """
        #query = """
        #    SELECT d.nombre, d.experiencia
        #    FROM docentes d
        #    JOIN docente_habilidades dh ON d.id = dh.id_docente
        #    JOIN habilidades h ON dh.id_habilidad = h.id
        #    WHERE h.habilidad = %s AND d.experiencia >= %s
        #"""
        #cursor.execute(query, (habilidad_usuario, experiencia_usuario))
        cursor.execute(query, (experiencia_usuario,))
        docentes = cursor.fetchall()
        cursor.close()
        
        ###docentes_similares = [...]  # Lógica de consulta a la base de datos

        # Calcular similitud entre habilidad del usuario y habilidad del docente
        similitudes = []
        for docente in docentes:
            habilidades_docente = docente[-1].split(', ')  # Obtener habilidades del docente y dividirlas en una lista
            #max_similitud = max(self.calcular_similitud(habilidad_usuario, habilidad_docente) for habilidad_docente in habilidades_docente)
            #similitudes.append((docente, max_similitud))
            max_similitud = max(self.calcular_similitud(
                fuzz.ratio(habilidad_usuario, habilidad_docente),  # Convertir la similitud de string a un valor fuzzy
                fuzz.ratio(habilidad_usuario, habilidad_docente),
                docente[2]  # Experiencia del docente
            ) for habilidad_docente in habilidades_docente)
            similitudes.append(({
                'id': docente[0],
                'nombre': docente[1],
                'experiencia': docente[2],
                'habilidades': docente[3]
            }, max_similitud))

            #for habilidad_docente in habilidades_docente:
            #    similitud = self.calcular_similitud(habilidad_usuario, habilidad_docente)
                #similitud = self.calcular_similitud(habilidad_usuario, docente['nombre'])
            #    similitudes.append((docente, similitud))

        # Ordenar docentes por similitud descendente
        similitudes.sort(key=lambda x: x[1], reverse=True)

        # Devolver un diccionario con la estructura {'docentes': [...]}
        #return [docente for docente, _ in similitudes]
        #docentes = [(resultado[0], resultado[1], resultado[2], habilidades) for resultado, habilidades in similitudes]
        #return {'docentes': [docente for docente, _ in similitudes]}
        #return {'docentes': [docente[0] for docente, _ in similitudes]}  # Return only unique docentes
        return {'docentes': [docente for docente, _ in similitudes]}  # Retornar solo los docentes

# Crear una instancia de Flask para manejar la lógica de la ontología difusa
app = Flask(__name__)

# Crear una instancia de la clase OntologiaFuzzy
ontologia_fuzzy = OntologiaFuzzy()

# Definir una ruta API para manejar la solicitud de búsqueda inteligente
@app.route('/api/ontologia_fuzzy', methods=['POST'])
def api_ontologia_fuzzy():
    data = request.get_json()  # Obtener los datos de la solicitud JSON
    habilidad = data['habilidad']
    experiencia = data['experiencia']
    docentes_similares = ontologia_fuzzy.obtener_docentes_similares(habilidad, experiencia)
    return jsonify(docentes_similares)

# Ejecutar la aplicación Flask
if __name__ == '__main__':
    app.run(debug=True)