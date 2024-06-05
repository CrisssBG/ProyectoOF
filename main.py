# main.py
from app import app
from db import init_connection  # Importa la función para inicializar la conexión a MySQL
from docentes import docentes_bp  # Importa el Blueprint de docentes
from flask import Flask, jsonify, request
from ontologia_fuzzy import OntologiaFuzzy

# Inicializa la configuración de MySQL
init_connection(app)

# Registra el Blueprint de docentes
app.register_blueprint(docentes_bp)

#Settings
#app.secret_key = 'mysecretkey'

# Crear instancia de la ontología difusa
ontologia_fuzzy = OntologiaFuzzy()

# Ruta para buscar docentes similares usando la ontología difusa
@app.route('/api/ontologia_fuzzy', methods=['POST'])
def buscar_docentes_similares():
    data = request.json
    habilidad = data.get('habilidad')
    experiencia = data.get('experiencia')
    docentes_similares = ontologia_fuzzy.obtener_docentes_similares(habilidad, experiencia)
    return jsonify(docentes_similares)

# Ejecuta la aplicación
if __name__ == "__main__":
    app.run(debug=True)
    #app.run(port=3000, debug=True)