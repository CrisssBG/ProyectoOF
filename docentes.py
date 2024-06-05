#docentes.py
from flask import Flask, Blueprint, current_app, render_template, request, jsonify, redirect, url_for, flash
#from db import init_connection, mysql
from db import mysql
from ontologia_fuzzy import OntologiaFuzzy
# En la parte superior del archivo docentes.py
#from flask_sqlalchemy import SQLAlchemy

#db = SQLAlchemy()

#No puedo importarlas desde app.py
#app = Flask (__name__)
#init_connection(app)

# Define el Blueprint para las rutas de docentes
docentes_bp = Blueprint('docentes', __name__)

# Inicializa la ontología difusa
ontologia_fuzzy = OntologiaFuzzy()

#def init_docente(app):
    
#@app.get('/')
@docentes_bp.route('/')
def index():
    cur = mysql.connection.cursor()
    #cur.execute('SELECT * FROM docentes')
    cur.execute('''
        SELECT d.id, d.nombre, d.experiencia, d.universidades, d.nivel_academico, GROUP_CONCAT(h.habilidad SEPARATOR ', ') AS habilidades
        FROM docentes d
        LEFT JOIN docente_habilidades dh ON d.id = dh.id_docente
        LEFT JOIN habilidades h ON dh.id_habilidad = h.id
        GROUP BY d.id
    ''')
    data = cur.fetchall()
    cur.close()
    return render_template('index.html', contacts=data)

# Ruta para la página de búsqueda inteligente
@docentes_bp.route('/busqueda_inteligente', methods=['GET'])
def busqueda_inteligente():
    return render_template('busqueda_inteligente.html')

# Ruta para manejar la solicitud de búsqueda inteligente
@docentes_bp.route('/api/busqueda_inteligente', methods=['POST'])
def api_busqueda_inteligente():
    # Aquí maneja la lógica de búsqueda inteligente como se mostró antes
    habilidad = request.json.get('habilidad')
    experiencia = request.json.get('experiencia')
    #docentes_similares = ontologia_fuzzy.obtener_docentes_similares(habilidad, experiencia)

    docentes_similares = ontologia_fuzzy.obtener_docentes_similares(habilidad, experiencia)

    # Consulta a la base de datos para obtener docentes que coincidan con la búsqueda
    #docentes = db.session.query(Docente, func.GROUP_CONCAT(Habilidad.habilidad.label()).label('habilidades')) \
    #    .join(DocenteHabilidad, Docente.id == DocenteHabilidad.id_docente) \
    #    .join(Habilidad, DocenteHabilidad.id_habilidad == Habilidad.id) \
    #    .filter(Habilidad.habilidad == habilidad, Docente.experiencia >= experiencia) \
    #    .group_by(Docente.id) \
    #    .all()

    #cur.execute('''
    #    SELECT d.id, d.nombre, d.experiencia, GROUP_CONCAT(h.habilidad SEPARATOR ', ') AS habilidades
    #    FROM docentes d
    #    LEFT JOIN docente_habilidades dh ON d.id = dh.id_docente
    #    LEFT JOIN habilidades h ON dh.id_habilidad = h.id
    #    WHERE h.habilidad = %s AND d.experiencia >= %s
    #    GROUP BY d.id
    #''', (habilidad, experiencia))

    #docentes_similares = [{'id': docente[0].id, 'nombre': docente[0].nombre, 'experiencia': docente[0].experiencia, 'habilidades': docente[1].split(', ')} for docente in docentes]
    return jsonify(docentes_similares)

#@app.route('/add_contact', methods=['POST'])
@docentes_bp.route('/add_contact', methods=['POST'])
def add_contact():
    if request.method == 'POST':
        nombre = request.form['nombre']
        experiencia = request.form['experiencia']
        universidades = request.form['universidades']
        nivel_academico = request.form['nivel_academico']
        habilidades = request.form.getlist('habilidades[]')  # Obtener la lista de habilidades seleccionadas
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO docentes (nombre, experiencia, universidades, nivel_academico) VALUES (%s, %s, %s, %s)', 
            (nombre, experiencia, universidades, nivel_academico))
        mysql.connection.commit()
        docente_id = cur.lastrowid  # Obtener el ID del docente recién insertado
        # Insertar las habilidades del docente en la tabla de relación many-to-many
        for habilidad_id in habilidades:
            cur.execute('INSERT INTO docente_habilidades (id_docente, id_habilidad) VALUES (%s, %s)', (docente_id, habilidad_id))
        mysql.connection.commit()
        cur.close()
        flash('Contact Added Successfully')
        return redirect(url_for('docentes.index'))

#@app.route('/edit/<id>')
@docentes_bp.route('/edit/<id>')
def get_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM docentes WHERE id = %s', (id,))
    data = cur.fetchall()
    cur.close()
    return render_template('edit-contact.html', contact=data[0])

#@app.route('/update/<id>', methods=['POST'])
@docentes_bp.route('/update/<id>', methods=['POST'])
def update_contact(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        experiencia = request.form['experiencia']
        universidades = request.form['universidades']
        nivel_academico = request.form['nivel_academico']
        habilidades = request.form.getlist('habilidades[]')  # Obtener la lista de habilidades seleccionadas
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE docentes
            SET nombre = %s,
                experiencia = %s,
                universidades = %s,
                nivel_academico = %s
            WHERE id = %s
        """, (nombre, experiencia, universidades, nivel_academico, id))

        # Eliminar todas las habilidades existentes del docente
        cur.execute("DELETE FROM docente_habilidades WHERE id_docente = %s", (id,))
        
        # Insertar las habilidades seleccionadas del docente en la tabla de relación many-to-many
        for habilidad_id in habilidades:
            cur.execute('INSERT INTO docente_habilidades (id_docente, id_habilidad) VALUES (%s, %s)', (id, habilidad_id))
        mysql.connection.commit()
        
        cur.close()

        flash('Docente Updated Successfully')
        return redirect(url_for('docentes.index'))

#@app.route('/delete/<string:id>')
@docentes_bp.route('/delete/<string:id>')
def delete_contact(id):
    cur = mysql.connection.cursor()
    #cur.execute('DELETE FROM docentes WHERE id = %s', (id,))
    #cur.execute('DELETE FROM docentes WHERE id = {0}'.format(id))
    #cur.execute('DELETE FROM docente_habilidades WHERE id_docente = {0}'.format(id))
    cur.execute('DELETE FROM docentes WHERE id = %s', (id,))
    cur.execute('DELETE FROM docente_habilidades WHERE id_docente = %s', (id,))
    mysql.connection.commit()
    flash('Contact Removed Successfully')
    return redirect(url_for('docentes.index'))