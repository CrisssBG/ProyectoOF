# main.py
from app import app
from db import init_connection, mysql  # Importa la función para inicializar la conexión a MySQL
from docentes import docentes_bp  # Importa el Blueprint de docentes
from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session, send_file
from ontologia_fuzzy import OntologiaFuzzy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import re
import uuid
from openpyxl import Workbook #Descargar en Excel
import os
from functools import wraps
#---Datos Difusos---#
import numpy as np
import skfuzzy as fuzz
import skfuzzy.control as ctrl
#from skfuzzy import control as ctrl
#from fuzzywuzzy import fuzz
#-------------------#

# Inicializa la configuración de MySQL
init_connection(app)

# Registra el Blueprint de docentes
app.register_blueprint(docentes_bp)

#Settings
app.secret_key = 'mysecretkey'

#Cargar la carpeta
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/images/profile_pics')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Extensiones permitidas para las imágenes

# resultado_difuso_global = None  # Variable global para almacenar el resultado difuso

# ######################################################################################
# Inicialización del sistema de control difuso
techniques_skills_proyecto = ['dev_software', 'dev_front_end', 'dev_back_end']

# # Definición de los antecedentes (habilidades de Desarrollo y Arquitectura de Software)
antecedents_techniques_skills = {
    skill: ctrl.Antecedent(np.arange(0, 101, 1), f"{skill.lower()}_score") for skill in techniques_skills_proyecto
}

# # Definición de las funciones de membresía para cada habilidad de Desarrollo y Arquitectura de Software
for skill in techniques_skills_proyecto:
    antecedents_techniques_skills[skill]['bajo'] = fuzz.trimf(antecedents_techniques_skills[skill].universe, [0, 0, 50])
    antecedents_techniques_skills[skill]['medio'] = fuzz.trimf(antecedents_techniques_skills[skill].universe, [0, 50, 100])
    antecedents_techniques_skills[skill]['alto'] = fuzz.trimf(antecedents_techniques_skills[skill].universe, [50, 100, 100])

# # Definición del consecuente (resultado de habilidades de Desarrollo y Arquitectura de Software)
resultado_techniques_skills = ctrl.Consequent(np.arange(0, 101, 1), 'resultado_techniques_skills')
resultado_techniques_skills['bajo'] = fuzz.trimf(resultado_techniques_skills.universe, [0, 0, 50])
resultado_techniques_skills['medio'] = fuzz.trimf(resultado_techniques_skills.universe, [50, 70, 85])
resultado_techniques_skills['alto'] = fuzz.trimf(resultado_techniques_skills.universe, [85, 100, 100])

# # Definición de reglas difusas
rules_techniques_skills = [
    ctrl.Rule(antecedents_techniques_skills['dev_software']['alto'] & antecedents_techniques_skills['dev_front_end']['alto'] & antecedents_techniques_skills['dev_back_end']['alto'], resultado_techniques_skills['alto']),
    ctrl.Rule(antecedents_techniques_skills['dev_software']['medio'] | antecedents_techniques_skills['dev_front_end']['medio'] | antecedents_techniques_skills['dev_back_end']['bajo'], resultado_techniques_skills['medio']),
    ctrl.Rule(antecedents_techniques_skills['dev_software']['bajo'] & antecedents_techniques_skills['dev_front_end']['bajo'] & antecedents_techniques_skills['dev_back_end']['medio'], resultado_techniques_skills['bajo']),

    # ctrl.Rule(antecedents_techniques_skills['dev_software']['alto'] & (antecedents_techniques_skills['dev_front_end']['medio'] | antecedents_techniques_skills['dev_back_end']['medio']), resultado_techniques_skills['medio']),
    ctrl.Rule(antecedents_techniques_skills['dev_software']['medio'] & antecedents_techniques_skills['dev_front_end']['alto'] & antecedents_techniques_skills['dev_back_end']['alto'], resultado_techniques_skills['alto']),
    ctrl.Rule(antecedents_techniques_skills['dev_software']['bajo'] & antecedents_techniques_skills['dev_front_end']['bajo'] & antecedents_techniques_skills['dev_back_end']['bajo'], resultado_techniques_skills['bajo']),

    ctrl.Rule(antecedents_techniques_skills['dev_software']['alto'] & antecedents_techniques_skills['dev_front_end']['bajo'] & antecedents_techniques_skills['dev_back_end']['bajo'], resultado_techniques_skills['medio']),
    ctrl.Rule(antecedents_techniques_skills['dev_software']['bajo'] & antecedents_techniques_skills['dev_front_end']['alto'] & antecedents_techniques_skills['dev_back_end']['bajo'], resultado_techniques_skills['medio']),
    ctrl.Rule(antecedents_techniques_skills['dev_software']['bajo'] & antecedents_techniques_skills['dev_front_end']['bajo'] & antecedents_techniques_skills['dev_back_end']['alto'], resultado_techniques_skills['medio']),

    ctrl.Rule(antecedents_techniques_skills['dev_software']['medio'] & antecedents_techniques_skills['dev_front_end']['alto'] & antecedents_techniques_skills['dev_back_end']['alto'], resultado_techniques_skills['alto']),
    ctrl.Rule(antecedents_techniques_skills['dev_software']['alto'] & antecedents_techniques_skills['dev_front_end']['medio'] & antecedents_techniques_skills['dev_back_end']['alto'], resultado_techniques_skills['alto']),
    ctrl.Rule(antecedents_techniques_skills['dev_software']['alto'] & antecedents_techniques_skills['dev_front_end']['alto'] & antecedents_techniques_skills['dev_back_end']['medio'], resultado_techniques_skills['alto']),

    ctrl.Rule(antecedents_techniques_skills['dev_software']['alto'] & (antecedents_techniques_skills['dev_front_end']['alto'] | antecedents_techniques_skills['dev_back_end']['alto']), resultado_techniques_skills['alto']),
    ctrl.Rule(antecedents_techniques_skills['dev_software']['alto'] & antecedents_techniques_skills['dev_front_end']['medio'] & antecedents_techniques_skills['dev_back_end']['medio'], resultado_techniques_skills['alto']),
    ctrl.Rule(antecedents_techniques_skills['dev_software']['medio'] & antecedents_techniques_skills['dev_front_end']['alto'] & antecedents_techniques_skills['dev_back_end']['medio'], resultado_techniques_skills['alto']),
    ctrl.Rule(antecedents_techniques_skills['dev_software']['medio'] & antecedents_techniques_skills['dev_front_end']['medio'] & antecedents_techniques_skills['dev_back_end']['alto'], resultado_techniques_skills['alto']),

    # ctrl.Rule(antecedents_techniques_skills['dev_software']['alto'] & antecedents_techniques_skills['dev_front_end']['medio'] & antecedents_techniques_skills['dev_back_end']['medio'], resultado_techniques_skills['medio']),
    # ctrl.Rule(antecedents_techniques_skills['dev_software']['medio'] & (antecedents_techniques_skills['dev_front_end']['alto'] | antecedents_techniques_skills['dev_back_end']['alto']), resultado_techniques_skills['medio']),
    # ctrl.Rule(antecedents_techniques_skills['dev_software']['medio'] & antecedents_techniques_skills['dev_front_end']['medio'] & antecedents_techniques_skills['dev_back_end']['medio'], resultado_techniques_skills['medio'])
]

# # Creación del sistema de control difuso
sistema_control_techniques_skills = ctrl.ControlSystem(rules_techniques_skills)

# # Creación de la simulación del sistema de control Habilidades Tecnicas
evaluador_techniques_skills = ctrl.ControlSystemSimulation(sistema_control_techniques_skills)
evaluador_techniques_skills_g = ctrl.ControlSystemSimulation(sistema_control_techniques_skills)
evaluador_techniques_skills_d = ctrl.ControlSystemSimulation(sistema_control_techniques_skills)
evaluador_techniques_skills_s = ctrl.ControlSystemSimulation(sistema_control_techniques_skills)
evaluador_techniques_skills_i = ctrl.ControlSystemSimulation(sistema_control_techniques_skills)
# Habilidades Blandas
evaluador_techniques_skills_bhl = ctrl.ControlSystemSimulation(sistema_control_techniques_skills)
evaluador_techniques_skills_bhc = ctrl.ControlSystemSimulation(sistema_control_techniques_skills)
evaluador_techniques_skills_bhi = ctrl.ControlSystemSimulation(sistema_control_techniques_skills)
evaluador_techniques_skills_bhm = ctrl.ControlSystemSimulation(sistema_control_techniques_skills)
# Habilidades Extracurriculares
evaluador_techniques_skills_ecd = ctrl.ControlSystemSimulation(sistema_control_techniques_skills)
evaluador_techniques_skills_eec = ctrl.ControlSystemSimulation(sistema_control_techniques_skills)
evaluador_techniques_skills_edp = ctrl.ControlSystemSimulation(sistema_control_techniques_skills)
evaluador_techniques_skills_eit = ctrl.ControlSystemSimulation(sistema_control_techniques_skills)
###########################################################################################

# # Valores de ejemplo para las habilidades de diseño del diseñador
# software_valor = 8
# front_end_valor = 6
# back_end_valor = 4

# # Aquí defines los valores de entrada que quieres probar
# evaluador_techniques_skills.input['dev_software_score'] = software_valor
# evaluador_techniques_skills.input['dev_front_end_score'] = front_end_valor
# evaluador_techniques_skills.input['dev_back_end_score'] = back_end_valor

# # Ejecutar la simulación del sistema de control
# evaluador_techniques_skills.compute()

# # Obtener el resultado
# resultado_difuso = evaluador_techniques_skills.output['resultado_techniques_skills']
# print(f"Resultado de habilidades de Desarrollo y Arquitectura de Software: {resultado_difuso}")





# # # Asignación de valores a los antecedentes
# # evaluador_techniques_skills.input['dev_software_score'] = 7
# # evaluador_techniques_skills.input['dev_front_end_score'] = 3
# # evaluador_techniques_skills.input['dev_back_end_score'] = 9

# # # Ejecución de la simulación
# # evaluador_techniques_skills.compute()

# # # Obtener los valores de entrada
# # dev_software_value = evaluador_techniques_skills.input['dev_software_score'].astype(int)
# # dev_front_end_value = evaluador_techniques_skills.input['dev_front_end_score'].astype(int)
# # dev_back_end_value = evaluador_techniques_skills.input['dev_back_end_score'].astype(int)

# # # Resultados de la simulación
# # resultado_techniques_skills_value = evaluador_techniques_skills.output['resultado_techniques_skills'].astype(int)

# # # Imprimir resultados
# # print("Valor de dev_software:", dev_software_value)
# # print("Valor de dev_front_end:", dev_front_end_value)
# # print("Valor de dev_back_end:", dev_back_end_value)
# # print("Resultado de habilidades de diseño:", resultado_techniques_skills_value)

# # # Visualización de la distribución de salida
# # resultado_techniques_skills.view(sim=evaluador_techniques_skills)
# resultado.view(sim=evaluador_techniques_skills)
###########################################################################################

# Crear instancia de la ontología difusa
#ontologia_fuzzy = OntologiaFuzzy()

#Decorador para que no se pueda ingresar a pestañas mientras no este iniciado sesion
def login_required(func):
    """
    Decorador para requerir inicio de sesión.
    Redirige al usuario a la página de inicio de sesión si no ha iniciado sesión.
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Por favor, inicia sesión para acceder a esta página', 'info')
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return decorated_function

# Ruta para buscar docentes similares usando la ontología difusa
#@app.route('/api/ontologia_fuzzy', methods=['POST'])
#@login_required
#def buscar_docentes_similares():
#    data = request.json
#    habilidad = data.get('habilidad')
#    experiencia = data.get('experiencia')
#    docentes_similares = ontologia_fuzzy.obtener_docentes_similares(habilidad, experiencia)
#    return jsonify(docentes_similares)



# Definición del sistema de control difuso
# Definir las antecedentes, consecuentes y reglas según tus requisitos específicos
# En este ejemplo, se usa un sistema de control difuso simple para habilidades técnicas

# # Definición de las antecedentes (habilidades técnicas)
# antecedents_skills = {
#     'software': ctrl.Antecedent(np.arange(0, 101, 1), 'software_score'),
#     'front_end': ctrl.Antecedent(np.arange(0, 101, 1), 'front_end_score'),
#     'back_end': ctrl.Antecedent(np.arange(0, 101, 1), 'back_end_score')
# }

# # Definición de las funciones de membresía para cada habilidad técnica
# # Ajusta según tus necesidades específicas
# for skill in antecedents_skills:
#     antecedents_skills[skill]['bajo'] = fuzz.trimf(antecedents_skills[skill].universe, [0, 0, 50])
#     antecedents_skills[skill]['medio'] = fuzz.trimf(antecedents_skills[skill].universe, [0, 50, 100])
#     antecedents_skills[skill]['alto'] = fuzz.trimf(antecedents_skills[skill].universe, [50, 100, 100])

# # Definición del consecuente (resultado de habilidades técnicas)
# resultado_skills = ctrl.Consequent(np.arange(0, 101, 1), 'resultado_skills')
# resultado_skills['bajo'] = fuzz.trimf(resultado_skills.universe, [0, 0, 50])
# resultado_skills['medio'] = fuzz.trimf(resultado_skills.universe, [25, 50, 75])
# resultado_skills['alto'] = fuzz.trimf(resultado_skills.universe, [50, 100, 100])

# # Definición de reglas difusas (ejemplo)
# rules_skills = [
#     # ctrl.Rule(antecedents_skills['software']['alto'] & antecedents_skills['front_end']['alto'], resultado_skills['alto']),
#     # ctrl.Rule(antecedents_skills['software']['medio'] | antecedents_skills['front_end']['medio'] | antecedents_skills['back_end']['bajo'], resultado_skills['medio']),
#     # ctrl.Rule(antecedents_skills['software']['bajo'] & antecedents_skills['front_end']['bajo'], resultado_skills['bajo'])

#     ctrl.Rule(antecedents_skills['software']['alto'] & antecedents_skills['front_end']['alto'], resultado_skills['alto']),
#     ctrl.Rule(antecedents_skills['software']['medio'] | antecedents_skills['front_end']['medio'] | antecedents_skills['back_end']['bajo'], resultado_skills['medio']),
#     ctrl.Rule(antecedents_skills['software']['bajo'] & antecedents_skills['front_end']['bajo'], resultado_skills['bajo']),

#     ctrl.Rule(antecedents_skills['software']['alto'] & (antecedents_skills['front_end']['medio'] | antecedents_skills['back_end']['medio']), resultado_skills['medio']),
#     ctrl.Rule(antecedents_skills['software']['medio'] & antecedents_skills['front_end']['alto'] & antecedents_skills['back_end']['alto'], resultado_skills['alto']),
#     ctrl.Rule(antecedents_skills['software']['bajo'] & antecedents_skills['front_end']['bajo'] & antecedents_skills['back_end']['bajo'], resultado_skills['bajo']),

#     ctrl.Rule(antecedents_skills['software']['alto'] & antecedents_skills['front_end']['bajo'] & antecedents_skills['back_end']['bajo'], resultado_skills['medio']),
#     ctrl.Rule(antecedents_skills['software']['bajo'] & antecedents_skills['front_end']['alto'] & antecedents_skills['back_end']['bajo'], resultado_skills['medio']),
#     ctrl.Rule(antecedents_skills['software']['bajo'] & antecedents_skills['front_end']['bajo'] & antecedents_skills['back_end']['alto'], resultado_skills['medio']),

#     ctrl.Rule(antecedents_skills['software']['medio'] & antecedents_skills['front_end']['alto'] & antecedents_skills['back_end']['alto'], resultado_skills['alto']),
#     ctrl.Rule(antecedents_skills['software']['alto'] & antecedents_skills['front_end']['medio'] & antecedents_skills['back_end']['alto'], resultado_skills['alto']),
#     ctrl.Rule(antecedents_skills['software']['alto'] & antecedents_skills['front_end']['alto'] & antecedents_skills['back_end']['medio'], resultado_skills['alto'])
# ]

# # Creación del sistema de control difuso
# sistema_control_skills = ctrl.ControlSystem(rules_skills)
# evaluador_skills = ctrl.ControlSystemSimulation(sistema_control_skills)




@app.route('/')
def home():
    if 'logged_in' in session:
        return redirect(url_for('index'))
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE email = %s', (email,))
    user = cursor.fetchone()
    cursor.close()  # Cerrar el cursor después de la consulta

    if user and check_password_hash(user[4], password):  # user[4] is the password field
        session['logged_in'] = True
        session['user_id'] = user[0]  # user[0] is the user ID field
        session['username'] = user[3]  # user[3] is the username field
        session['email'] = user[2]  # user[2] is the email field
        flash('Has iniciado sesión correctamente', 'success')
        #if session['id_rol']==1:
        #    return render_template('admin.html')
        #elif session['id_rol']==2:
        #    return redirect(url_for('index'))
        return redirect(url_for('index'))
    else:
        flash('Correo o contraseña incorrectos', 'danger')
    return redirect(url_for('home'))

@app.route('/registeruser', methods=['POST'])
def registeruser():
    name = request.form['name']
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    #cedula = request.form['cedula']

    #------------------------------------------------------#
     # Dividir nombre_completo en nombre y apellido
    partes_nombre = name.split()
    if len(partes_nombre) >= 4:
        nombre = ' '.join(partes_nombre[:2]) # Tomamos los dos primeros elementos como el nombre completo
        apellido = ' '.join(partes_nombre[2:])
    elif len(partes_nombre) == 2 or len(partes_nombre) == 3:
        nombre = partes_nombre[0]
        apellido = ' '.join(partes_nombre[1:])
    else:
        nombre = name
        apellido = ''
    #------------------------------------------------------#

    cursor = mysql.connection.cursor()

    #------------------------------------------------------#
    #Verificar si el usuario y cedula ya está registrado
    cursor.execute('SELECT * FROM usuarios WHERE email = %s', (email,))
    existing_user = cursor.fetchone()
    if existing_user:
        flash('Correo electrónico ya está registrado', 'danger')
        return redirect(url_for('home'))

    cursor.execute('SELECT * FROM docente WHERE cedula = %s', (username,))
    existing_cedula = cursor.fetchone()
    if existing_cedula:
        flash('Número de cédula ya está registrado', 'danger')
        return redirect(url_for('home'))

    #------------------------------------------------------#

    #------------------------------------------------------#
    # Si no existen registros previos de correo electrónico ni de username, procede con el registro
    hashed_password = generate_password_hash(password)
    cursor.execute('INSERT INTO usuarios (nombre_completo, email, usuario, password) VALUES (%s, %s, %s, %s)',
                   (name, email, username, hashed_password))
    mysql.connection.commit()
    #------------------------------------------------------#

    #------------------------------------------------------#
    # Verificar si el user/cédula ya está registrado
    ##cursor.execute('SELECT * FROM usuarios WHERE usuario = %s', (username,))
    ##existing_username = cursor.fetchone()
    ##if existing_username:
    ##    flash('Número de cédula ya está registrado', 'danger')
    ##    return redirect(url_for('home'))
    #------------------------------------------------------#

    #-------------------------------------------------------#
    # Obtener el ID del usuario recién registrado
    cursor.execute('SELECT id FROM usuarios WHERE email = %s', (email,))
    user_id = cursor.fetchone()[0]

    # Insertar en la tabla docente
    cursor.execute('INSERT INTO docente (id_usuario, nombre, apellido, cedula, email) VALUES (%s, %s, %s, %s, %s)',
                   (user_id, nombre, apellido, username, email))
    mysql.connection.commit()
    #--------------------------------------------------------#
    # Obtener el ID del docente recién insertado
    #cursor.execute('SELECT id FROM docente WHERE id_usuario = %s', (user_id,))
    #docente_id = cursor.fetchone()[0]
    # Insertar en la tabla habilidades_t_b
    #cursor.execute('INSERT INTO habilidades_t_b (id_usuario) VALUES (%s)', (docente_id))
    #mysql.connection.commit()
    #--------------------------------------------------------#
    # Obtener el ID del docente recién insertado
    cursor.execute('SELECT id FROM docente WHERE id_usuario = %s', (user_id,))
    docente_id = cursor.fetchone()[0]

    cursor.execute('INSERT INTO habilidades_t_b (id_docente ) VALUES (%s)', (docente_id,))
    mysql.connection.commit()
    #--------------------------------------------------------#
    # Obtener el ID del docente recién insertado
    cursor.execute('SELECT id FROM habilidades_t_b WHERE id_docente = %s', (docente_id,))
    habilidades_t_b_id = cursor.fetchone()[0]

    cursor.execute('INSERT INTO resultados_difusos_h_t (id_habilidades_t_b ) VALUES (%s)', (habilidades_t_b_id,))
    mysql.connection.commit()

    #--------------------------------------------------------#
    cursor.execute('INSERT INTO intereses (id_docente ) VALUES (%s)', (docente_id,))
    mysql.connection.commit()

    cursor.close()
    flash('Registro exitoso, ahora puedes iniciar sesión', 'success')
    return redirect(url_for('home'))

@app.route('/index')
@login_required
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT imagen_p FROM docente WHERE id_usuario = %s", [session['user_id']])
    data = cur.fetchone()
    cur.close()
    # # Si 'data' es None, significa que el usuario no tiene imagen de perfil guardada
    imagen_p = data[0] if data else None
    # # Ahora pasas 'imagen_p' como parte del contexto al renderizar el template
    return render_template('ini.html', imagen_p=imagen_p if imagen_p else 'default.png')
    # try:
    #     # Obtener imagen de perfil del docente
    #     cur = mysql.connection.cursor()
    #     cur.execute("SELECT imagen_p FROM docente WHERE id_usuario = %s", [session['user_id']])
    #     data = cur.fetchone()
    #     cur.close()

    #     # Si 'data' es None, asignamos una imagen por defecto
    #     imagen_p = data[0] if data else 'default.png'

    #     # Lógica para obtener y evaluar habilidades técnicas del docente
    #     cur = mysql.connection.cursor()
    #     cur.execute("SELECT * FROM habilidades_t_b WHERE id_docente = %s", [session['user_id']])
    #     habilidades_data = cur.fetchone()
    #     cur.close()

    #     resultado_difuso = None

    #     if habilidades_data:
    #         # Obtener los valores de habilidades técnicas del docente
    #         software_valor = habilidades_data[3]  # Ajustar según el índice correcto de la columna
    #         front_end_valor = habilidades_data[9]  # Ajustar según el índice correcto de la columna
    #         back_end_valor = habilidades_data[10]  # Ajustar según el índice correcto de la columna

    #         #evaluador_skills = ctrl.ControlSystemSimulation(evaluador)

    #         # Establecer los valores de entrada en la simulación del evaluador difuso
    #         evaluador_skills.input['software_score'] = software_valor
    #         evaluador_skills.input['front_end_score'] = front_end_valor
    #         evaluador_skills.input['back_end_score'] = back_end_valor

    #         # Ejecutar la simulación del sistema de control difuso
    #         evaluador_skills.compute()

    #         # Obtener el resultado difuso de las habilidades técnicas
    #         resultado_difuso = evaluador_skills.output['resultado_skills']

    #         # Renderizar el template con la imagen de perfil y el resultado difuso
    #         return render_template('index.html', imagen_p=imagen_p, resultado_difuso=resultado_difuso)
    #     else:
    #         flash('No se encontraron habilidades técnicas para este usuario', 'warning')

    # except Exception as e:
    #     flash(f'Ocurrió un error al cargar la página: {str(e)}', 'danger')

    # return redirect(url_for('home'))


@app.route('/logout', methods=['GET', 'POST'] )
#@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('home'))

@app.route('/perfil')
@login_required
def perfil():
    #global resultado_difuso
    try:
        # Obtener datos del usuario desde la tabla usuarios
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id, nombre, apellido, email FROM docente WHERE id_usuario = %s', (session['user_id'],))
        user = cursor.fetchone()
        #cursor.close()

        if user:
            #name = user[0]
            #nombre_completo = user[0]
            id_docente = user[0]
            nombre = user[1]
            apellido = user[2]
            #email = user[1]
            email = user[3]

            # Dividir nombre_completo en nombre y apellido
            #partes_nombre = nombre_completo.split()
            #if len(partes_nombre) >= 3:
            #    nombre = ' '.join(partes_nombre[:2])  # Primer Nombre y Segundo Nombre
            #    apellido = ' '.join(partes_nombre[2:])  # Primer Apellido y Segundo Apellido
            #elif len(partes_nombre) == 2:
            #    nombre = partes_nombre[0]
            #    apellido = partes_nombre[1]
            #else:
            #    nombre = nombre_completo
            #    apellido = ''

            # Obtener datos adicionales del docente desde la tabla docente
            cursor.execute('SELECT cedula, celular, genero, nvl_estudio, carrera, imagen_p, disponibilidad_c, anios_exp_informatica FROM docente WHERE id_usuario = %s', (session['user_id'],))
            #cursor.execute('SELECT cedula, celular, genero, nvl_estudio, carrera, imagen_p, disponibilidad_c FROM docente WHERE id = %s', (id_docente,))
            docente_data = cursor.fetchone()

            if docente_data:
                cedula = docente_data[0] if docente_data[0] else ""
                celular = docente_data[1] if docente_data[1] else ""
                genero = docente_data[2] if docente_data[2] else ""
                nvl_estudio = docente_data[3] if docente_data[3] else ""
                carrera = docente_data[4] if docente_data[4] else ""
                imagen_p = docente_data[5] if docente_data[5] else 'default.png'  # Imagen predeterminada
                disponibilidad_c = docente_data[6] if docente_data[6] else "0"
                anios_exp_informatica = docente_data[7] if docente_data[6] else ""

                # Convertir imagen_p a cadena str si es bytes
                #if isinstance(imagen_p, bytes):
                #    imagen_p = imagen_p.decode('utf-8')

                cursor.execute('SELECT tipos_intereses, otros FROM intereses WHERE id_docente = %s', (id_docente,))
                result  = cursor.fetchone()

                if result:
                    tipos_intereses = result[0]
                    otros = result[1]
                    
                    # Verificar si tipos_intereses es None o una cadena vacía
                    if tipos_intereses:
                        # Dividir la cadena en una lista de intereses
                        intereses = tipos_intereses.split(',')
                    else:
                        intereses = []
                    
                    # Verificar si otros es None o una cadena vacía
                    if otros:
                        # No es necesario dividir, simplemente asigna el valor
                        texto_otros = otros
                    else:
                        texto_otros = ""
                else:
                    intereses = []
                    texto_otros = ""

                # if result:
                #     tipos_intereses = result[0]
                #     otros = result[1]
                #     # Verificar si tipos_intereses es None
                #     if tipos_intereses:
                #         # Dividir la cadena en una lista de intereses
                #         intereses = tipos_intereses.split(',')
                #     else:
                #         intereses = []
                # else:
                #     intereses = []

                # Obtener habilidades técnicas y blandas del docente
                cursor.execute('SELECT * FROM habilidades_t_b WHERE id_docente = %s', (id_docente,))
                habilidades_data = cursor.fetchone()

                habilidades_tecnicas = {}
                habilidades_blandas = {}
                habilidades_extracurriculares = {}
                
                #Resultado Habilidades Tecnicas
                resultado_difuso = 0
                resultado_difuso_g = 0
                resultado_difuso_d = 0
                resultado_difuso_s = 0
                resultado_difuso_i = 0
                #Resultado Habilidades Blandas
                resultado_difuso_bhl = 0
                resultado_difuso_bhc = 0
                resultado_difuso_bhi = 0
                resultado_difuso_bhm = 0
                #Resultado Habilidades Extracurriculares
                resultado_difuso_ecd = 0
                resultado_difuso_eec = 0
                resultado_difuso_edp = 0
                resultado_difuso_eit = 0

                if habilidades_data:
                    habilidades_tecnicas = {
                        'desarrollo_software': habilidades_data[2],
                        'desarrollo_frontend': habilidades_data[3],
                        'desarrollo_backend': habilidades_data[4],
                        'redes': habilidades_data[5],
                        'analisis_datos': habilidades_data[6],
                        'gestion_base_datos': habilidades_data[7],
                        'business_intelligence_bi': habilidades_data[8],
                        'sistemas_operativos': habilidades_data[9],
                        'disenio_interfaz': habilidades_data[10],
                        'animacion_grafica': habilidades_data[11],
                        'prototipado': habilidades_data[12],
                        'administracion_servidores': habilidades_data[13],
                        'seguridad_informatica': habilidades_data[14],
                        'gestion_servidores_nube': habilidades_data[15],
                        'criptografia': habilidades_data[16],
                        'aprendizaje_automatico_machine_learning': habilidades_data[17],
                    }

                    habilidades_blandas = {
                        'comunicacion_asertiva': habilidades_data[18],
                        'trabajo_equipo': habilidades_data[19],
                        'resolucion_problemas': habilidades_data[20],
                        'adaptabilidad': habilidades_data[21],
                        'empatia': habilidades_data[22],
                        'tolerancia_estres': habilidades_data[23],
                        'creatividad': habilidades_data[24],
                        'liderazgo': habilidades_data[25],
                        'gestion_tiempo': habilidades_data[26],
                        'resiliencia': habilidades_data[27],
                        'pensamiento_critico': habilidades_data[28],
                        'manejo_inteligencia_emocional': habilidades_data[29],
                    }

                    habilidades_extracurriculares = {
                        'manejo_redes_sociales': habilidades_data[30],
                        'marketing_digital': habilidades_data[31],
                        'edicion_video': habilidades_data[32],
                        'idiomas_extranjeros': habilidades_data[33],
                        'tecnicas_presentacion': habilidades_data[34],
                        'redaccion_creativa': habilidades_data[35],
                        'diseno_grafico': habilidades_data[36],
                        'fotografia': habilidades_data[37],
                        'animacion_3d': habilidades_data[38],
                        'negociacion': habilidades_data[39],
                        'habilidades_ventas': habilidades_data[40],
                        'mindfulness_meditacion': habilidades_data[41],
                    }

                    # Resultado Difuso Habilidades Técnicas

                    if (habilidades_tecnicas['desarrollo_software'] is not None and
                        habilidades_tecnicas['desarrollo_frontend'] is not None and
                        habilidades_tecnicas['desarrollo_backend'] is not None and
                        habilidades_tecnicas['redes'] is not None and
                        habilidades_tecnicas['analisis_datos'] is not None and
                        habilidades_tecnicas['gestion_base_datos'] is not None and
                        habilidades_tecnicas['business_intelligence_bi'] is not None and
                        habilidades_tecnicas['sistemas_operativos'] is not None and
                        habilidades_tecnicas['disenio_interfaz'] is not None and
                        habilidades_tecnicas['animacion_grafica'] is not None and
                        habilidades_tecnicas['prototipado'] is not None and
                        habilidades_tecnicas['administracion_servidores'] is not None and
                        habilidades_tecnicas['seguridad_informatica'] is not None and
                        habilidades_tecnicas['gestion_servidores_nube'] is not None and
                        habilidades_tecnicas['criptografia'] is not None and
                        habilidades_tecnicas['aprendizaje_automatico_machine_learning'] is not None):

                        # Aquí defines los valores de entrada que quieres probar
                        evaluador_techniques_skills.input['dev_software_score'] = habilidades_tecnicas['desarrollo_software']
                        evaluador_techniques_skills.input['dev_front_end_score'] = habilidades_tecnicas['desarrollo_frontend']
                        evaluador_techniques_skills.input['dev_back_end_score'] = habilidades_tecnicas['desarrollo_backend']

                        # Ejecutar la simulación del sistema de control
                        evaluador_techniques_skills.compute()

                        # Obtener el resultado
                        resultado_difuso = evaluador_techniques_skills.output['resultado_techniques_skills']
                        # print(f"Resultado de habilidades de Desarrollo y Arquitectura de Software: {resultado_difuso}")

                        # Gestión y Análisis de Datos:
                        evaluador_techniques_skills_g.input['dev_software_score'] = habilidades_tecnicas['analisis_datos']
                        evaluador_techniques_skills_g.input['dev_front_end_score'] = habilidades_tecnicas['gestion_base_datos']
                        evaluador_techniques_skills_g.input['dev_back_end_score'] = habilidades_tecnicas['business_intelligence_bi']
                        evaluador_techniques_skills_g.compute()
                        resultado_difuso_g = evaluador_techniques_skills_g.output['resultado_techniques_skills']

                        # Diseño de Interfaz y Multimedia:
                        evaluador_techniques_skills_d.input['dev_software_score'] = habilidades_tecnicas['disenio_interfaz']
                        evaluador_techniques_skills_d.input['dev_front_end_score'] = habilidades_tecnicas['animacion_grafica']
                        evaluador_techniques_skills_d.input['dev_back_end_score'] = habilidades_tecnicas['prototipado']
                        evaluador_techniques_skills_d.compute()
                        resultado_difuso_d = evaluador_techniques_skills_d.output['resultado_techniques_skills']

                        # Seguridad y Cloud Computing:
                        evaluador_techniques_skills_s.input['dev_software_score'] = habilidades_tecnicas['seguridad_informatica']
                        evaluador_techniques_skills_s.input['dev_front_end_score'] = habilidades_tecnicas['gestion_servidores_nube']
                        evaluador_techniques_skills_s.input['dev_back_end_score'] = habilidades_tecnicas['criptografia']
                        evaluador_techniques_skills_s.compute()
                        resultado_difuso_s = evaluador_techniques_skills_s.output['resultado_techniques_skills']

                        # Infraestructura y Comunicaciones:
                        evaluador_techniques_skills_i.input['dev_software_score'] = habilidades_tecnicas['redes']
                        evaluador_techniques_skills_i.input['dev_front_end_score'] = habilidades_tecnicas['sistemas_operativos']
                        evaluador_techniques_skills_i.input['dev_back_end_score'] = habilidades_tecnicas['administracion_servidores']
                        evaluador_techniques_skills_i.compute()
                        resultado_difuso_i = evaluador_techniques_skills_i.output['resultado_techniques_skills']

                        #Guardar Resultados Difusos
                        # Ejemplo de cómo actualizar los resultados difusos en la base de datos
                        cursor.execute("""
                            UPDATE resultados_difusos_h_t
                            SET resultado_difuso = %s,
                                resultado_difuso_g = %s,
                                resultado_difuso_d = %s,
                                resultado_difuso_s = %s,
                                resultado_difuso_i = %s
                            WHERE id_habilidades_t_b = %s
                        """, (
                            resultado_difuso,
                            resultado_difuso_g,
                            resultado_difuso_d,
                            resultado_difuso_s,
                            resultado_difuso_i,
                            habilidades_data[0]  # Asegúrate de que habilidades_data[0] sea el id de habilidades_t_b
                        ))

                        mysql.connection.commit()  # Guardar los cambios en la base de datos

                    # Resultado Difuso Habilidades Blandas

                    if (habilidades_blandas['comunicacion_asertiva'] is not None and
                        habilidades_blandas['trabajo_equipo'] is not None and
                        habilidades_blandas['resolucion_problemas'] is not None and
                        habilidades_blandas['adaptabilidad'] is not None and
                        habilidades_blandas['empatia'] is not None and
                        habilidades_blandas['tolerancia_estres'] is not None and
                        habilidades_blandas['creatividad'] is not None and
                        habilidades_blandas['liderazgo'] is not None and
                        habilidades_blandas['gestion_tiempo'] is not None and
                        habilidades_blandas['resiliencia'] is not None and
                        habilidades_blandas['pensamiento_critico'] is not None and
                        habilidades_blandas['manejo_inteligencia_emocional'] is not None):

                        # print(f"Habilidades Blandas: {habilidades_blandas}")

                        # Aquí defines los valores de entrada Habilidad de Liderazgo Efectivo
                        evaluador_techniques_skills_bhl.input['dev_software_score'] = habilidades_blandas['liderazgo']
                        evaluador_techniques_skills_bhl.input['dev_front_end_score'] = habilidades_blandas['gestion_tiempo']
                        evaluador_techniques_skills_bhl.input['dev_back_end_score'] = habilidades_blandas['resolucion_problemas']
                        evaluador_techniques_skills_bhl.compute()
                        resultado_difuso_bhl = evaluador_techniques_skills_bhl.output['resultado_techniques_skills']

                        # Habilidad de Comunicación y Relaciones Interpersonales
                        evaluador_techniques_skills_bhc.input['dev_software_score'] = habilidades_blandas['comunicacion_asertiva']
                        evaluador_techniques_skills_bhc.input['dev_front_end_score'] = habilidades_blandas['trabajo_equipo']
                        evaluador_techniques_skills_bhc.input['dev_back_end_score'] = habilidades_blandas['empatia']
                        evaluador_techniques_skills_bhc.compute()
                        resultado_difuso_bhc = evaluador_techniques_skills_bhc.output['resultado_techniques_skills']

                        # Habilidad de Innovación y Creatividad
                        evaluador_techniques_skills_bhi.input['dev_software_score'] = habilidades_blandas['creatividad']
                        evaluador_techniques_skills_bhi.input['dev_front_end_score'] = habilidades_blandas['pensamiento_critico']
                        evaluador_techniques_skills_bhi.input['dev_back_end_score'] = habilidades_blandas['adaptabilidad']
                        evaluador_techniques_skills_bhi.compute()
                        resultado_difuso_bhi = evaluador_techniques_skills_bhi.output['resultado_techniques_skills']

                        # Habilidad de Manejo y Bienestar Personal
                        evaluador_techniques_skills_bhm.input['dev_software_score'] = habilidades_blandas['tolerancia_estres']
                        evaluador_techniques_skills_bhm.input['dev_front_end_score'] = habilidades_blandas['resiliencia']
                        evaluador_techniques_skills_bhm.input['dev_back_end_score'] = habilidades_blandas['manejo_inteligencia_emocional']
                        evaluador_techniques_skills_bhm.compute()
                        resultado_difuso_bhm = evaluador_techniques_skills_bhm.output['resultado_techniques_skills']

                        #Guardar Resultados Difusos
                        # Ejemplo de cómo actualizar los resultados difusos en la base de datos
                        cursor.execute("""
                            UPDATE resultados_difusos_h_t
                            SET resultado_difuso_bhl = %s,
                                resultado_difuso_bhc = %s,
                                resultado_difuso_bhi = %s,
                                resultado_difuso_bhm = %s
                            WHERE id_habilidades_t_b = %s
                        """, (
                            resultado_difuso_bhl,
                            resultado_difuso_bhc,
                            resultado_difuso_bhi,
                            resultado_difuso_bhm,
                            habilidades_data[0]  # Asegúrate de que habilidades_data[0] sea el id de habilidades_t_b
                        ))

                        mysql.connection.commit()  # Guardar los cambios en la base de datos

                    # Resultado Difuso Habilidades Extracurriculares

                    if (habilidades_extracurriculares['manejo_redes_sociales'] is not None and
                        habilidades_extracurriculares['marketing_digital'] is not None and
                        habilidades_extracurriculares['edicion_video'] is not None and
                        habilidades_extracurriculares['idiomas_extranjeros'] is not None and
                        habilidades_extracurriculares['tecnicas_presentacion'] is not None and
                        habilidades_extracurriculares['redaccion_creativa'] is not None and
                        habilidades_extracurriculares['diseno_grafico'] is not None and
                        habilidades_extracurriculares['fotografia'] is not None and
                        habilidades_extracurriculares['animacion_3d'] is not None and
                        habilidades_extracurriculares['negociacion'] is not None and
                        habilidades_extracurriculares['habilidades_ventas'] is not None and
                        habilidades_extracurriculares['mindfulness_meditacion'] is not None):

                        # print(f"Habilidades Blandas: {habilidades_blandas}")

                        # Aquí defines los valores de entrada Habilidad de Liderazgo Efectivo
                        evaluador_techniques_skills_ecd.input['dev_software_score'] = habilidades_extracurriculares['diseno_grafico']
                        evaluador_techniques_skills_ecd.input['dev_front_end_score'] = habilidades_extracurriculares['edicion_video']
                        evaluador_techniques_skills_ecd.input['dev_back_end_score'] = habilidades_extracurriculares['fotografia']
                        evaluador_techniques_skills_ecd.compute()
                        resultado_difuso_ecd = evaluador_techniques_skills_ecd.output['resultado_techniques_skills']

                        # Habilidad de Comunicación y Relaciones Interpersonales
                        evaluador_techniques_skills_eec.input['dev_software_score'] = habilidades_extracurriculares['manejo_redes_sociales']
                        evaluador_techniques_skills_eec.input['dev_front_end_score'] = habilidades_extracurriculares['marketing_digital']
                        evaluador_techniques_skills_eec.input['dev_back_end_score'] = habilidades_extracurriculares['redaccion_creativa']
                        evaluador_techniques_skills_eec.compute()
                        resultado_difuso_eec = evaluador_techniques_skills_eec.output['resultado_techniques_skills']

                        # Habilidad de Innovación y Creatividad
                        evaluador_techniques_skills_edp.input['dev_software_score'] = habilidades_extracurriculares['tecnicas_presentacion']
                        evaluador_techniques_skills_edp.input['dev_front_end_score'] = habilidades_extracurriculares['negociacion']
                        evaluador_techniques_skills_edp.input['dev_back_end_score'] = habilidades_extracurriculares['habilidades_ventas']
                        evaluador_techniques_skills_edp.compute()
                        resultado_difuso_edp = evaluador_techniques_skills_edp.output['resultado_techniques_skills']

                        # Habilidad de Manejo y Bienestar Personal
                        evaluador_techniques_skills_eit.input['dev_software_score'] = habilidades_extracurriculares['idiomas_extranjeros']
                        evaluador_techniques_skills_eit.input['dev_front_end_score'] = habilidades_extracurriculares['animacion_3d']
                        evaluador_techniques_skills_eit.input['dev_back_end_score'] = habilidades_extracurriculares['mindfulness_meditacion']
                        evaluador_techniques_skills_eit.compute()
                        resultado_difuso_eit = evaluador_techniques_skills_eit.output['resultado_techniques_skills']

                        #Guardar Resultados Difusos
                        # Ejemplo de cómo actualizar los resultados difusos en la base de datos
                        cursor.execute("""
                            UPDATE resultados_difusos_h_t
                            SET resultado_difuso_ecd = %s,
                                resultado_difuso_eec = %s,
                                resultado_difuso_edp = %s,
                                resultado_difuso_eit = %s
                            WHERE id_habilidades_t_b = %s
                        """, (
                            resultado_difuso_ecd,
                            resultado_difuso_eec,
                            resultado_difuso_edp,
                            resultado_difuso_eit,
                            habilidades_data[0]  # Asegúrate de que habilidades_data[0] sea el id de habilidades_t_b
                        ))

                        mysql.connection.commit()  # Guardar los cambios en la base de datos


                cursor.close()

                return render_template('perfil.html', nombre=nombre, apellido=apellido, email=email, cedula=cedula, celular=celular, genero=genero, nvl_estudio=nvl_estudio, carrera=carrera, imagen_p=imagen_p, disponibilidad_c=disponibilidad_c, anios_exp_informatica=anios_exp_informatica, intereses=intereses, texto_otros=texto_otros, habilidades_tecnicas=habilidades_tecnicas, habilidades_blandas=habilidades_blandas, habilidades_extracurriculares=habilidades_extracurriculares, resultado_difuso=resultado_difuso, resultado_difuso_g=resultado_difuso_g, resultado_difuso_d=resultado_difuso_d, resultado_difuso_s=resultado_difuso_s, resultado_difuso_i=resultado_difuso_i, resultado_difuso_bhl=resultado_difuso_bhl, resultado_difuso_bhc=resultado_difuso_bhc, resultado_difuso_bhi=resultado_difuso_bhi, resultado_difuso_bhm=resultado_difuso_bhm, resultado_difuso_ecd=resultado_difuso_ecd, resultado_difuso_eec=resultado_difuso_eec, resultado_difuso_edp=resultado_difuso_edp, resultado_difuso_eit=resultado_difuso_eit)
            else:
                flash('No se encontraron datos del docente para este usuario', 'warning')
        else:
            flash('Usuario no encontrado', 'danger')
    except Exception as e:
        flash(f'Ocurrió un error al cargar la página: {str(e)}', 'danger')

    return redirect(url_for('index'))

#@app.route('/uploads/<path:filename>')
#def uploaded_file(filename):
#    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/register')
@login_required
def register():
    # Tu lógica para la vista 'register' aquí

    #return redirect(url_for('home'))
    #return render_template('index.html')
    return render_template('register.html')


# def busqueda():
#     if request.method == 'POST':
#         # Establecemos el tipo de búsqueda directamente en cada función de búsqueda
#         tipo_busqueda = request.form.get('tipo_busqueda')

#         try:
#             if tipo_busqueda == 'inteligente':
#                 return busqueda_inteligente()
#             elif tipo_busqueda == 'avanzada':
#                 return busqueda_avanzada()
#             elif tipo_busqueda == 'ia':
#                 return busqueda_ia()
#             else:
#                 raise ValueError("Tipo de búsqueda no reconocido")
#         except Exception as e:
#             print(f"Error: {e}")
#             return render_template('busqueda.html', tipo_busqueda=tipo_busqueda, imagen_p='default.png', error=str(e))

#     # Si la solicitud es GET, simplemente renderizamos el formulario de búsqueda
#     return render_template('busqueda.html', tipo_busqueda='inteligente', imagen_p='default.png')



@app.route('/busqueda_inteligente', methods=['GET', 'POST'])
@login_required
def busqueda_inteligente():
    imagen_p = 'default.png'  # Valor por defecto inicial
    tipo_busqueda = 'inteligente'
    if request.method == 'POST':
        try:
            #tipo_busqueda = request.form.get('tipo_busqueda', 'inteligente')
            # Capturar los valores enviados desde el formulario
            desarrollo_arquitectura = float(request.form.get('desarrollo_arquitectura'))
            gestion_analisis_datos = float(request.form.get('gestion_analisis_datos'))
            disenio_interfaz_multimedia = float(request.form.get('disenio_interfaz_multimedia'))
            seguridad_cloud_computing = float(request.form.get('seguridad_cloud_computing'))
            infraestructura_comunicaciones = float(request.form.get('infraestructura_comunicaciones'))

            habilidad_liderazgo_efectivo = float(request.form.get('habilidad_liderazgo_efectivo'))
            habilidad_comunicacion_relaciones_i = float(request.form.get('habilidad_comunicacion_relaciones_i'))
            habilidad_innovacion_creatividad = float(request.form.get('habilidad_innovacion_creatividad'))
            habilidad_manejo_bienestar_personal = float(request.form.get('habilidad_manejo_bienestar_personal'))
            creacion_contenidos_visuales = float(request.form.get('creacion_contenidos_visuales'))
            estrategia_medios_digitales = float(request.form.get('estrategia_medios_digitales'))
            desarrollo_profesional = float(request.form.get('desarrollo_profesional'))
            idiomas_tecnicas_relajacion = float(request.form.get('idiomas_tecnicas_relajacion'))

            # Capturar el nivel de estudio
            #nivel_estudio = request.form.get('nivel_estudio')
            nivel_estudio = request.form.getlist('nivel_estudio')

            print("Datos recibidos:")
            print(f"Desarrollo Arquitectura: {desarrollo_arquitectura}")
            print(f"Gestión Análisis Datos: {gestion_analisis_datos}")
            print(f"Diseño Interfaz Multimedia: {disenio_interfaz_multimedia}")
            print(f"Seguridad Cloud Computing: {seguridad_cloud_computing}")
            print(f"Infrastructura Comunicaciones: {infraestructura_comunicaciones}")
            print(f"Habilidad Liderazgo Efectivo: {habilidad_liderazgo_efectivo}")
            print(f"Habilidad Comunicación Relaciones I: {habilidad_comunicacion_relaciones_i}")
            print(f"Habilidad Innovación Creatividad: {habilidad_innovacion_creatividad}")
            print(f"Habilidad Manejo Bienestar Personal: {habilidad_manejo_bienestar_personal}")
            print(f"Creación Contenidos Visuales: {creacion_contenidos_visuales}")
            print(f"Estrategia Medios Digitales: {estrategia_medios_digitales}")
            print(f"Desarrollo Profesional: {desarrollo_profesional}")
            print(f"Idiomas Técnicas Relajación: {idiomas_tecnicas_relajacion}")
            print(f"Niveles de Estudio: {nivel_estudio}")

            # Consulta SQL para obtener id_habilidades_t_b de resultados_difusos_h_t
            cursor = mysql.connection.cursor()
            
            try:
                #Extraer imagen de nuevo de la session imagen_pb?
                cursor.execute('SELECT imagen_p FROM docente WHERE id_usuario = %s', (session['user_id'],))
                imagen_p_result  = cursor.fetchone()
                if imagen_p_result :    # Extraer la imagen de perfil si está disponible
                    imagen_p = imagen_p_result[0]  # Asigna el primer elemento de la tupla
                    #session['imagen_p'] = imagen_p  # Almacena en la sesión
                else:
                    imagen_p = 'default.png'  # Si no hay imagen, asigna una imagen predeterminada
                    #session['imagen_p'] = imagen_p  # Almacena en la sesión

                # Establecer en la sesión
                # session['imagen_p'] = imagen_p

                # Consulta para obtener datos de resultados_difusos_h_t
                sql_resultados = """
                    SELECT id_habilidades_t_b, resultado_difuso, resultado_difuso_g, resultado_difuso_d, resultado_difuso_s, resultado_difuso_i, resultado_difuso_bhl, resultado_difuso_bhc, resultado_difuso_bhi, resultado_difuso_bhm, resultado_difuso_ecd, resultado_difuso_eec, resultado_difuso_edp, resultado_difuso_eit
                    FROM resultados_difusos_h_t 
                    WHERE (resultado_difuso BETWEEN %s AND %s
                    OR resultado_difuso_g BETWEEN %s AND %s
                    OR resultado_difuso_d BETWEEN %s AND %s
                    OR resultado_difuso_s BETWEEN %s AND %s
                    OR resultado_difuso_i BETWEEN %s AND %s
                    OR resultado_difuso_bhl BETWEEN %s AND %s
                    OR resultado_difuso_bhc BETWEEN %s AND %s
                    OR resultado_difuso_bhi BETWEEN %s AND %s
                    OR resultado_difuso_bhm BETWEEN %s AND %s
                    OR resultado_difuso_ecd BETWEEN %s AND %s
                    OR resultado_difuso_eec BETWEEN %s AND %s
                    OR resultado_difuso_edp BETWEEN %s AND %s
                    OR resultado_difuso_eit BETWEEN %s AND %s)
                """
                parametros = (
                    desarrollo_arquitectura - 5, desarrollo_arquitectura + 5,
                    gestion_analisis_datos - 5, gestion_analisis_datos + 5,
                    disenio_interfaz_multimedia - 5, disenio_interfaz_multimedia + 5,
                    seguridad_cloud_computing - 5, seguridad_cloud_computing + 5,
                    infraestructura_comunicaciones - 5, infraestructura_comunicaciones + 5,
                    habilidad_liderazgo_efectivo - 5, habilidad_liderazgo_efectivo + 5,
                    habilidad_comunicacion_relaciones_i - 5, habilidad_comunicacion_relaciones_i + 5,
                    habilidad_innovacion_creatividad - 5, habilidad_innovacion_creatividad + 5,
                    habilidad_manejo_bienestar_personal - 5, habilidad_manejo_bienestar_personal + 5,
                    creacion_contenidos_visuales - 5, creacion_contenidos_visuales + 5,
                    estrategia_medios_digitales - 5, estrategia_medios_digitales + 5,
                    desarrollo_profesional - 5, desarrollo_profesional + 5,
                    idiomas_tecnicas_relajacion - 5, idiomas_tecnicas_relajacion + 5,
                )
                cursor.execute(sql_resultados, parametros)

                resultados_difusos = cursor.fetchall()

                print("Resultados Difusos:")
                for resultado in resultados_difusos:
                    print(resultado)

                if resultados_difusos:
                    # Crear listas vacías para almacenar los resultados
                    id_habilidades_t_b_list = []
                    resultado_difuso_list = []
                    resultado_difuso_g_list = []
                    resultado_difuso_d_list = []
                    resultado_difuso_s_list = []
                    resultado_difuso_i_list = []
                    resultado_difuso_bhl_list = []
                    resultado_difuso_bhc_list = []
                    resultado_difuso_bhi_list = []
                    resultado_difuso_bhm_list = []
                    resultado_difuso_ecd_list = []
                    resultado_difuso_eec_list = []
                    resultado_difuso_edp_list = []
                    resultado_difuso_eit_list = []

                    for row in resultados_difusos:
                        id_habilidades_t_b_list.append(row[0])
                        resultado_difuso_list.append(row[1])
                        resultado_difuso_g_list.append(row[2])
                        resultado_difuso_d_list.append(row[3])
                        resultado_difuso_s_list.append(row[4])
                        resultado_difuso_i_list.append(row[5])
                        resultado_difuso_bhl_list.append(row[6])
                        resultado_difuso_bhc_list.append(row[7])
                        resultado_difuso_bhi_list.append(row[8])
                        resultado_difuso_bhm_list.append(row[9])
                        resultado_difuso_ecd_list.append(row[10])
                        resultado_difuso_eec_list.append(row[11])
                        resultado_difuso_edp_list.append(row[12])
                        resultado_difuso_eit_list.append(row[13])

                    # Calcular porcentaje de similitud (coeficiente de Jaccard)
                    def coeficiente_jaccard(set1, set2):
                        keys = set(set1.keys()).union(set(set2.keys()))
                        inter = sum(min(set1.get(k, 0), set2.get(k, 0)) for k in keys)
                        union = sum(max(set1.get(k, 0), set2.get(k, 0)) for k in keys)
                        return inter / union if union else 0

                    # Calcular porcentaje de similitud (coeficiente de Jaccard)
                    valores_formulario = {
                        'desarrollo_arquitectura': desarrollo_arquitectura,
                        'gestion_analisis_datos': gestion_analisis_datos,
                        'disenio_interfaz_multimedia': disenio_interfaz_multimedia,
                        'seguridad_cloud_computing': seguridad_cloud_computing,
                        'infraestructura_comunicaciones': infraestructura_comunicaciones,
                        'habilidad_liderazgo_efectivo': habilidad_liderazgo_efectivo,
                        'habilidad_comunicacion_relaciones_i': habilidad_comunicacion_relaciones_i,
                        'habilidad_innovacion_creatividad': habilidad_innovacion_creatividad,
                        'habilidad_manejo_bienestar_personal': habilidad_manejo_bienestar_personal,
                        'creacion_contenidos_visuales': creacion_contenidos_visuales,
                        'estrategia_medios_digitales': estrategia_medios_digitales,
                        'desarrollo_profesional': desarrollo_profesional,
                        'idiomas_tecnicas_relajacion': idiomas_tecnicas_relajacion
                    }

                    resultados_difusos_h_t_list = []
                    for i in range(len(resultado_difuso_list)):
                        resultados_difusos_h_t = {
                            'desarrollo_arquitectura': resultado_difuso_list[i],
                            'gestion_analisis_datos': resultado_difuso_g_list[i],
                            'disenio_interfaz_multimedia': resultado_difuso_d_list[i],
                            'seguridad_cloud_computing': resultado_difuso_s_list[i],
                            'infraestructura_comunicaciones': resultado_difuso_i_list[i],
                            'habilidad_liderazgo_efectivo': resultado_difuso_bhl_list[i],
                            'habilidad_comunicacion_relaciones_i': resultado_difuso_bhc_list[i],
                            'habilidad_innovacion_creatividad': resultado_difuso_bhi_list[i],
                            'habilidad_manejo_bienestar_personal': resultado_difuso_bhm_list[i],
                            'creacion_contenidos_visuales': resultado_difuso_ecd_list[i],
                            'estrategia_medios_digitales': resultado_difuso_eec_list[i],
                            'desarrollo_profesional': resultado_difuso_edp_list[i],
                            'idiomas_tecnicas_relajacion': resultado_difuso_eit_list[i]
                        }
                        resultados_difusos_h_t_list.append(resultados_difusos_h_t)

                    similitud_list = []
                    for resultados_difusos_h_t in resultados_difusos_h_t_list:
                        similitud = coeficiente_jaccard(valores_formulario, resultados_difusos_h_t)
                        similitud_list.append(similitud)

                    nivel_confianza_list = [similitud * 100 for similitud in similitud_list]

                    sql_docentes = """
                    SELECT d.nombre, d.apellido, d.cedula, d.celular, d.email, d.genero, d.nvl_estudio, d.carrera, d.imagen_p, d.disponibilidad_c, d.anios_exp_informatica
                        FROM docente d
                        JOIN habilidades_t_b ht ON d.id = ht.id_docente
                        JOIN resultados_difusos_h_t rd ON ht.id = rd.id_habilidades_t_b
                        WHERE (rd.resultado_difuso BETWEEN %s AND %s
                        OR rd.resultado_difuso_g BETWEEN %s AND %s
                        OR rd.resultado_difuso_d BETWEEN %s AND %s
                        OR rd.resultado_difuso_s BETWEEN %s AND %s
                        OR rd.resultado_difuso_i BETWEEN %s AND %s
                        OR rd.resultado_difuso_bhl BETWEEN %s AND %s
                        OR rd.resultado_difuso_bhc BETWEEN %s AND %s
                        OR rd.resultado_difuso_bhi BETWEEN %s AND %s
                        OR rd.resultado_difuso_bhm BETWEEN %s AND %s
                        OR rd.resultado_difuso_ecd BETWEEN %s AND %s
                        OR rd.resultado_difuso_eec BETWEEN %s AND %s
                        OR rd.resultado_difuso_edp BETWEEN %s AND %s
                        OR rd.resultado_difuso_eit BETWEEN %s AND %s)
                        AND ("""
                        
                    # Agregar condiciones dinámicas para cada nivel seleccionado
                    condiciones = []
                    parametros_docentes = list(parametros)  # Copia de la lista de parámetros para los docentes
                    for index, nivel in enumerate(nivel_estudio):
                        if index > 0:
                            sql_docentes += " OR "
                        sql_docentes += "FIND_IN_SET(%s, d.nvl_estudio)"
                        condiciones.append(nivel)
                        parametros_docentes.append(nivel)
                    
                    sql_docentes += ") LIMIT 10;"
                    cursor.execute(sql_docentes, parametros_docentes)

                    #cursor.execute(sql_docentes, parametros)
                    docentes_data = cursor.fetchall()

                    print("Datos de Docentes:")
                    for docente in docentes_data:
                        print(docente)

                    # Ordenar docentes, resultados_difusos y demás datos según nivel_confianza_list
                    datos_completos = list(zip(
                        docentes_data, 
                        id_habilidades_t_b_list,
                        resultado_difuso_list, 
                        resultado_difuso_g_list,
                        resultado_difuso_d_list,
                        resultado_difuso_s_list,
                        resultado_difuso_i_list,
                        resultado_difuso_bhl_list,
                        resultado_difuso_bhc_list,
                        resultado_difuso_bhi_list,
                        resultado_difuso_bhm_list,
                        resultado_difuso_ecd_list,
                        resultado_difuso_eec_list,
                        resultado_difuso_edp_list,
                        resultado_difuso_eit_list,
                        similitud_list,
                        nivel_confianza_list
                    ))

                    # Ordenar por nivel_confianza_list (último elemento en la tupla)
                    datos_completos.sort(key=lambda x: x[-1], reverse=True)
                    docentes_data, id_habilidades_t_b_list, resultado_difuso_list, resultado_difuso_g_list, resultado_difuso_d_list, resultado_difuso_s_list, resultado_difuso_i_list, resultado_difuso_bhl_list, resultado_difuso_bhc_list, resultado_difuso_bhi_list, resultado_difuso_bhm_list, resultado_difuso_ecd_list, resultado_difuso_eec_list, resultado_difuso_edp_list, resultado_difuso_eit_list, similitud_list, nivel_confianza_list = zip(*datos_completos)
                    
                    if docentes_data:
                        # imagen_pb = docente_data[8]
                        docentes = []
                        for docente_data in docentes_data:
                            # imagen_pb = docente_data[8]
                            docente = {
                                'nombre': docente_data[0],
                                'apellido': docente_data[1],
                                'cedula': docente_data[2],
                                'celular': docente_data[3],
                                'email': docente_data[4],
                                'genero': docente_data[5],
                                'nvl_estudio': docente_data[6] if docente_data[6] else '',
                                'carrera': docente_data[7] if docente_data[7] else '',
                                'imagen_pb': docente_data[8],
                                'disponibilidad_c': docente_data[9] if docente_data[9] else '',
                                'anios_exp_informatica': docente_data[10] if docente_data[10] else ''
                            }
                            docentes.append(docente)
                            #imagen_pb = docente_data[8]
                    else:
                        docentes = None
                    #imagen_pb = None

                    # cursor.close()
                    # print('Imagen de perfil:', imagen_p)}

                    # Redirigir a la misma página con parámetros de búsqueda
                    # search_params = {
                    #     'desarrollo_arquitectura': desarrollo_arquitectura,
                    #     'gestion_analisis_datos': gestion_analisis_datos,
                    #     # (Omitido por brevedad: otros campos)
                    #     'nivel_estudio': ','.join(nivel_estudio)
                    # }
                    # search_query_string = '&'.join([f'{key}={value}' for key, value in search_params.items()])
                    # return redirect(url_for('busqueda_inteligente') + '?' + search_query_string)
                    
                    #docentes = obtener_docentes(tipo_busqueda)
                    #nivel_confianza_list = obtener_nivel_confianza(tipo_busqueda)
                    # Renderizar la plantilla con los resultados

                    flash('¡Búsqueda realizada correctamente!', 'success')

                    return render_template('busqueda_inteligente.html',
                                        docentes=docentes, id_habilidades_t_b_list=id_habilidades_t_b_list,
                                        resultado_difuso_list=resultado_difuso_list,
                                        resultado_difuso_g_list=resultado_difuso_g_list,
                                        resultado_difuso_d_list=resultado_difuso_d_list,
                                        resultado_difuso_s_list=resultado_difuso_s_list,
                                        resultado_difuso_i_list=resultado_difuso_i_list,
                                        resultado_difuso_bhl_list=resultado_difuso_bhl_list,
                                        resultado_difuso_bhc_list=resultado_difuso_bhc_list,
                                        resultado_difuso_bhi_list=resultado_difuso_bhi_list,
                                        resultado_difuso_bhm_list=resultado_difuso_bhm_list,
                                        resultado_difuso_ecd_list=resultado_difuso_ecd_list,
                                        resultado_difuso_eec_list=resultado_difuso_eec_list,
                                        resultado_difuso_edp_list=resultado_difuso_edp_list,
                                        resultado_difuso_eit_list=resultado_difuso_eit_list,
                                        similitud_list=similitud_list,
                                        nivel_confianza_list=nivel_confianza_list,
                                        # imagen_pb=imagen_pb,
                                        imagen_p=imagen_p, tipo_busqueda=tipo_busqueda)
                else:
                    # No se encontraron resultados
                    flash('No se encontraron coincidencias con la búsqueda ', 'danger')
                    return render_template('busqueda_inteligente.html', imagen_p=imagen_p, tipo_busqueda=tipo_busqueda)
            finally:
                cursor.close()
        except Exception as e:
            # Manejo de errores
            print(f"Error: {e}")
            return redirect(url_for('busqueda_inteligente', imagen_p=imagen_p))
            # return render_template('error.html', error=str(e))
        # return render_template('busqueda_inteligente.html')
    else:
        # Si el método es GET, simplemente renderiza el formulario
        return render_template('busqueda_inteligente.html', tipo_busqueda=tipo_busqueda, imagen_p=imagen_p)

#--------------------------------------------------------------------#
# Ruta para renderizar el perfil
#@app.route('/perfil', methods=['GET'])
#def mostrar_perfil():
    # Aquí deberías cargar los datos del perfil desde la base de datos o donde los tengas almacenados
    # Ejemplo de datos de perfil (esto dependerá de cómo estén almacenados en tu sistema)
#    perfil = {
#        'nombre': 'Juan',
#        'apellidos': 'Pérez',
#        'cedula': '1234567890',
#        'celular': '555-123-4567',
#        'correo': 'juan@example.com',
#        'genero': 'masculino',
#        'nivel_estudio': ['Universitario'],
#        'carreras': ['Ingeniería'],
#        'disponibilidad': 50,
#        'imagen_perfil': 'default.jpg',  # Nombre de archivo de imagen de perfil
#        'prog_programacion': 80,
#        'prog_desarrollo_software': 70,
#        'prog_analisis_datos': 60,
#        'prog_base_datos': 50,
#        'prog_diseño_grafico': 40,
#        'prog_redes': 30,
#        'prog_sistemas_operativos': 50,
#        'prog_front_end': 60,
#        'prog_back_end': 70
#    }

    # Renderizar la plantilla perfil.html y pasarle los datos del perfil
#    return render_template('perfil.html', **perfil)

@app.route('/busqueda_avanzada', methods=['GET', 'POST'])
@login_required
def busqueda_avanzada():
    tipo_busqueda = 'avanzada'
    imagen_p = 'default.png'  # Valor predeterminado
    if request.method == 'POST':
        try:
            # Capturar los valores enviados desde el formulario
            anios_exp_informatica = int(request.form.get('anios_exp_informatica'))
            nivel_estudio = request.form.getlist('nivel_estudio')
            habilidades_tecnicas_seleccionadas = request.form.getlist('habilidades_tecnicas')
            habilidades_blandas_seleccionadas = request.form.getlist('habilidades_blandas')
            habilidades_extracurriculares_seleccionadas = request.form.getlist('habilidades_extracurriculares')
            # habilidades_tecnicas = request.form.getlist('habilidades_tecnicas')
            # habilidades_blandas = request.form.getlist('habilidades_blandas')

            # # Asegúrate de convertir anios_exp_informatica a entero, si es necesario
            # try:
            #     anios_exp_informatica = int(anios_exp_informatica)
            # except (ValueError, TypeError) as e:
            #     print(f"Error al convertir años de experiencia: {e}")
            #     anios_exp_informatica = 0  # Valor por defecto o manejar el error

            # Imprimir los valores para depuración
            print(f"Años de experiencia: {anios_exp_informatica}")
            print(f"Nivel de estudio: {nivel_estudio}")
            print(f"Habilidades técnicas seleccionadas: {habilidades_tecnicas_seleccionadas}")
            print(f"Habilidades blandas seleccionadas: {habilidades_blandas_seleccionadas}")
            print(f"Habilidades extracurriculares seleccionadas: {habilidades_extracurriculares_seleccionadas}")

            # Consulta SQL para obtener id_habilidades_t_b de resultados_difusos_h_t
            cursor = mysql.connection.cursor()

            sql_docentes = """
                SELECT d.nombre, d.apellido, d.cedula, d.celular, d.email, d.genero, d.nvl_estudio, d.carrera, d.imagen_p, d.disponibilidad_c, d.anios_exp_informatica,
                    ht.desarrollo_software, ht.desarrollo_frontend, ht.desarrollo_backend, ht.redes, ht.analisis_datos,
                    ht.gestion_base_datos, ht.business_intelligence_bi, ht.sistemas_operativos, ht.disenio_interfaz, 
                    ht.animacion_grafica, ht.prototipado, ht.administracion_servidores, ht.seguridad_informatica, 
                    ht.gestion_servidores_nube, ht.criptografia, ht.aprendizaje_automatico_machine_learning,
                    ht.comunicacion_asertiva, ht.trabajo_equipo, ht.resolucion_problemas, ht.adaptabilidad, ht.empatia, ht.tolerancia_estres,
                    ht.creatividad, ht.liderazgo, ht.gestion_tiempo, ht.resiliencia, ht.pensamiento_critico, ht.manejo_inteligencia_emocional,
                    ht.manejo_redes_sociales, ht.marketing_digital, ht.edicion_video, ht.idiomas_extranjeros, ht.tecnicas_presentacion, ht.redaccion_creativa,
                    ht.diseno_grafico, ht.fotografia, ht.animacion_3d, ht.negociacion, ht.habilidades_ventas, ht.mindfulness_meditacion
                FROM docente d
                JOIN habilidades_t_b ht ON d.id = ht.id_docente
                WHERE d.anios_exp_informatica BETWEEN %s AND %s
            """
            
            parametros_docentes = [anios_exp_informatica, anios_exp_informatica + 10]

            # Añadir condiciones de nivel de estudio si se han seleccionado
            if nivel_estudio:
                sql_docentes += " AND ("
                condiciones = []
                for index, nivel in enumerate(nivel_estudio):
                    if index > 0:
                        sql_docentes += " OR "
                    sql_docentes += "FIND_IN_SET(%s, d.nvl_estudio)"
                    parametros_docentes.append(nivel)
                sql_docentes += ")"

            # Filtrar por habilidades técnicas y blandas seleccionadas
            habilidades_seleccionadas = habilidades_tecnicas_seleccionadas + habilidades_blandas_seleccionadas + habilidades_extracurriculares_seleccionadas
            if habilidades_seleccionadas:
                sql_docentes += " AND ("
                condiciones = [f"ht.{habilidad} IS NOT NULL" for habilidad in habilidades_seleccionadas]
                sql_docentes += " OR ".join(condiciones)
                sql_docentes += ")"

            # Añadir ordenamiento por habilidades técnicas y blandas seleccionadas
            if habilidades_seleccionadas:
                sql_docentes += " ORDER BY " + ", ".join([f"ht.{habilidad} DESC" for habilidad in habilidades_seleccionadas])
            else:
                sql_docentes += " ORDER BY d.nombre ASC"  # Ordenar por nombre si no hay habilidades seleccionadas

            sql_docentes += " LIMIT 10;"

            # Imprimir la consulta para depuración
            print(f"Consulta SQL generada: {sql_docentes}")
            print(f"Parámetros de la consulta: {parametros_docentes}")

            # Ejecutar la consulta
            cursor = mysql.connection.cursor()
            # Extraer imagen de perfil de la sesión
            cursor.execute('SELECT imagen_p FROM docente WHERE id_usuario = %s', (session['user_id'],))
            imagen_p_result = cursor.fetchone()
            if imagen_p_result:
                imagen_p = imagen_p_result[0]
            else:
                imagen_p = 'default.png'  # Si no hay imagen, asigna una imagen predeterminada
            print(f"Foto: {imagen_p}")

            # Ejecutar la consulta
            cursor.execute(sql_docentes, parametros_docentes)
            docentes_data = cursor.fetchall()
            #print(f'Tipo de Búsqueda: {tipo_busqueda}')  # Imprime en la consola para depuración

            # Imprimir los resultados para depuración
            print("Resultados de la consulta:")
            for docente in docentes_data:
                print(docente)

            # Cerrar el cursor
            cursor.close()

            if not docente:
                flash('No se encontraron coincidencias con la búsqueda', 'danger')
                return redirect(url_for('busqueda_inteligente'))

            # # Si no se encuentran docentes, establecer la imagen predeterminada
            # if not docentes_data:
            #     imagen_p
            # # else:
            # if tipo_busqueda in ['inteligente', 'avanzada', 'ia']:
            #     return redirect('/busqueda_general')
            # Renderizar la plantilla con los resultados
            #return redirect(url_for('busqueda_inteligente', docentes=docentes_data, habilidades_tecnicas=habilidades_tecnicas_seleccionadas, habilidades_blandas=habilidades_blandas_seleccionadas, tipo_busqueda=tipo_busqueda, imagen_p=imagen_p))
            flash('¡Búsqueda realizada correctamente!', 'success')
            return render_template('busqueda_inteligente.html', docentes=docentes_data, habilidades_tecnicas=habilidades_tecnicas_seleccionadas, habilidades_blandas=habilidades_blandas_seleccionadas, habilidades_extracurriculares_seleccionadas=habilidades_extracurriculares_seleccionadas, tipo_busqueda=tipo_busqueda, imagen_p=imagen_p)
    
        except Exception as e:
            # Manejo de errores
            print(f"Error: {e}")
            flash('No se encontraron coincidencias con la búsqueda', 'danger')
            return redirect(url_for('busqueda_inteligente'))
            #return redirect(url_for('busqueda_inteligente', tipo_busqueda=tipo_busqueda, imagen_p=imagen_p, error=str(e)))
            # return render_template('busqueda_inteligente.html', tipo_busqueda=tipo_busqueda, imagen_p=imagen_p, error=str(e))

    return render_template('busqueda_inteligente.html', tipo_busqueda=tipo_busqueda, imagen_p=imagen_p)



@app.route('/busqueda_ia', methods=['POST'])
@login_required
def busqueda_ia():
    mensaje = request.form.get('mensaje', '')
    tipo_busqueda = 'ia'
    imagen_p = 'default.png'  # Valor predeterminado

    try:
        # Validar que el mensaje no esté vacío
        if not mensaje:
            flash('El mensaje de búsqueda no puede estar vacío', 'danger')
            return redirect(url_for('busqueda_inteligente'))
        
        # Imprimir datos ingresados
        print(f"Mensaje recibido: {mensaje}")

        # Inicializar parámetros
        nivel_estudio = None
        habilidades = []
        anios_exp_minimos = 0

        # Procesar el mensaje de búsqueda
        # Mapeo de términos comunes a niveles de estudio
        niveles_estudio_map = {
            'tecnólogo': 'Tecnólogo',
            'licenciatura': 'Licenciatura',
            'especialización': 'Especialización',
            'maestría': 'Maestría',
            'doctorado': 'Doctorado',
            'posdoctorado': 'Posdoctorado',
            'ingeniero': 'Licenciatura',  # Ajustar según contexto
            'magíster': 'Maestría',
            'master': 'Maestría',
            'bachelor': 'Licenciatura',
            'doctor': 'Doctorado'
        }

        # Buscar nivel de estudio
        for termino, nivel in niveles_estudio_map.items():
            if re.search(termino, mensaje, re.IGNORECASE):
                nivel_estudio = nivel
                break

        # Buscar habilidades
        habilidades_posibles = [
            'Desarrollo Software', 'Desarrollo Frontend', 'Desarrollo Backend', 'Redes', 'Análisis de Datos',
            'Gestión Base de Datos', 'Business Intelligence (BI)', 'Sistemas Operativos', 'Diseño Interfaz',
            'Animación Gráfica', 'Prototipado', 'Administración Servidores', 'Seguridad Informática',
            'Gestión Servidores Nube', 'Criptografía', 'Aprendizaje Automático (Machine Learning)'
        ]
        habilidades = [h.replace(' ', '_').lower() for h in habilidades_posibles if re.search(h, mensaje, re.IGNORECASE)]

        # Buscar años de experiencia
        match = re.search(r'(\d+)\s*años?\s*de\s*experiencia', mensaje, re.IGNORECASE)
        if match:
            anios_exp_minimos = int(match.group(1))

        # Verificar si al menos uno de los parámetros de búsqueda es significativo
        if not nivel_estudio and not habilidades and anios_exp_minimos == 0:
            flash('No se encontraron parámetros válidos en la búsqueda', 'danger')
            return redirect(url_for('busqueda_inteligente'))

        # Construir consulta SQL basada en los parámetros extraídos
        cursor = mysql.connection.cursor()
        sql_docentes = """
            SELECT d.nombre, d.apellido, d.cedula, d.celular, d.email, d.genero, d.nvl_estudio, d.carrera, d.imagen_p, d.disponibilidad_c, d.anios_exp_informatica,
                ht.desarrollo_software, ht.desarrollo_frontend, ht.desarrollo_backend, ht.redes, ht.analisis_datos,
                ht.gestion_base_datos, ht.business_intelligence_bi, ht.sistemas_operativos, ht.disenio_interfaz, 
                ht.animacion_grafica, ht.prototipado, ht.administracion_servidores, ht.seguridad_informatica, 
                ht.gestion_servidores_nube, ht.criptografia, ht.aprendizaje_automatico_machine_learning,
                ht.comunicacion_asertiva, ht.trabajo_equipo, ht.resolucion_problemas, ht.adaptabilidad, ht.empatia, ht.tolerancia_estres,
                ht.creatividad, ht.liderazgo, ht.gestion_tiempo, ht.resiliencia, ht.pensamiento_critico, ht.manejo_inteligencia_emocional
            FROM docente d
            JOIN habilidades_t_b ht ON d.id = ht.id_docente
            WHERE d.anios_exp_informatica >= %s
        """
        parametros_docentes = [anios_exp_minimos]

        # Añadir condición de nivel de estudio
        if nivel_estudio:
            sql_docentes += " AND d.nvl_estudio LIKE %s"
            parametros_docentes.append(f"%{nivel_estudio}%")

        # Filtrar por habilidades seleccionadas
        if habilidades:
            sql_docentes += " AND ("
            condiciones = [f"ht.{habilidad.replace(' ', '_').lower()} IS NOT NULL" for habilidad in habilidades]
            sql_docentes += " OR ".join(condiciones)
            sql_docentes += ")"

        # Imprimir consulta SQL final y parámetros
        print(f"Consulta SQL: {sql_docentes}")
        print(f"Parámetros: {parametros_docentes}")

        # Ejecutar consulta
        cursor.execute(sql_docentes, parametros_docentes)
        docentes_data = cursor.fetchall()

        # Imprimir resultados de la consulta
        print(f"Datos de docentes: {docentes_data}")

        # Extraer imagen de perfil
        cursor.execute('SELECT imagen_p FROM docente WHERE id_usuario = %s', (session['user_id'],))
        imagen_p_result = cursor.fetchone()
        if imagen_p_result:
            imagen_p = imagen_p_result[0]
        else:
            imagen_p = 'default.png'

        cursor.close()

        # # Definir habilidades técnicas y blandas (ajusta según sea necesario)
        habilidades_tecnicas = [
            'desarrollo_software', 'desarrollo_frontend', 'desarrollo_backend', 'redes', 'analisis_datos',
            'gestion_base_datos', 'business_intelligence_bi', 'sistemas_operativos', 'disenio_interfaz',
            'animacion_grafica', 'prototipado', 'administracion_servidores', 'seguridad_informatica',
            'gestion_servidores_nube', 'criptografia', 'aprendizaje_automatico_machine_learning'
        ]
        habilidades_blandas = [
            'comunicacion_asertiva', 'trabajo_equipo', 'resolucion_problemas', 'adaptabilidad', 'empatia',
            'tolerancia_estres', 'creatividad', 'liderazgo', 'gestion_tiempo', 'resiliencia', 'pensamiento_critico',
            'manejo_inteligencia_emocional'
        ]

        # # Guardar datos en la sesión antes de redirigir
        # session['docentes_data'] = docentes_data
        # session['imagen_p'] = imagen_p
        # session['habilidades_tecnicas'] = habilidades_tecnicas
        # session['habilidades_blandas'] = habilidades_blandas

        if not docentes_data:
            flash('No se encontraron coincidencias con la búsqueda', 'danger')
            return redirect(url_for('busqueda_inteligente'))
        
        flash('¡Búsqueda realizada correctamente!', 'success')
        # Renderizar el template directamente
        return render_template('busqueda_inteligente.html',
                               tipo_busqueda=tipo_busqueda,
                               docentes_data=docentes_data,
                               imagen_p=imagen_p,
                               habilidades_tecnicas=habilidades_tecnicas,
                               habilidades_blandas=habilidades_blandas)

        # Redirigir a la página principal de búsqueda
        #return redirect(url_for('busqueda_inteligente'))

    except Exception as e:
        # Manejo de errores
        flash('No se encontraron coincidencias con la búsqueda', 'danger')
        print(f"Error: {e}")
        # Guardar información en la sesión para manejar el error en la página principal
        session['tipo_busqueda'] = tipo_busqueda
        session['imagen_p'] = imagen_p
        session['error'] = str(e)
        return redirect(url_for('busqueda_inteligente'))
    

@app.route('/buscar_intereses', methods=['POST'])
def buscar_intereses():
    imagen_p = 'default.png'  # Valor predeterminado
    tipo_busqueda = 'intereses'

    # Obtener el valor seleccionado del formulario
    tipos_intereses = request.form.get('tipos_intereses')

    # Validar que tipos_intereses no sea vacío
    if not tipos_intereses:
        # return jsonify({"error": "No se proporcionó ningún interés"}), 400  # Devuelve un error si el interés está vacío
        return redirect(url_for('busqueda_inteligente'))
    try:
        # Realizar la consulta a la base de datos con LIKE
        cursor = mysql.connection.cursor()
        query = """
            SELECT d.nombre, d.apellido, d.cedula, d.celular, d.email, d.genero, d.nvl_estudio, d.carrera, d.imagen_p, d.disponibilidad_c, i.tipos_intereses, i.otros
            FROM docente d
            JOIN intereses i ON d.id = i.id_docente
            WHERE i.tipos_intereses LIKE %s
        """
        cursor.execute(query, ('%' + tipos_intereses + '%',))
        resultados = cursor.fetchall()

        # Extraer imagen de perfil
        cursor.execute('SELECT imagen_p FROM docente WHERE id_usuario = %s', (session['user_id'],))
        imagen_p_result = cursor.fetchone()
        if imagen_p_result:
            imagen_p = imagen_p_result[0]
        else:
            imagen_p = 'default.png'

        cursor.close()

        print(f"Resultados de la búsqueda: {resultados}")
        
        if not resultados:
            flash('No se encontraron coincidencias con la búsqueda', 'danger')
            return redirect(url_for('busqueda_inteligente'))
            # return jsonify({"message": "No se encontraron resultados"}), 404  # Mensaje si no se encuentran resultados
        
        flash('¡Búsqueda realizada correctamente!', 'success')
        # Pasar los resultados al template
        return render_template('busqueda_inteligente.html', resultados=resultados, imagen_p=imagen_p, tipo_busqueda=tipo_busqueda)
    
    except Exception as e:
        # Manejo de errores
        # return jsonify({"error": str(e)}), 500  # Devuelve un error si ocurre una excepción
        # Manejo de errores
        flash('No se encontraron coincidencias con la búsqueda', 'danger')
        print(f"Error: {e}")
        session['imagen_p'] = imagen_p
        return redirect(url_for('busqueda_inteligente'))


# Ruta para guardar el perfil editado
@app.route('/guardar_perfil', methods=['POST'])
def guardar_perfil():
    # Aquí deberías guardar los datos editados del perfil en la base de datos o en tu sistema de almacenamiento
    if request.method == 'POST':
        # Obtener los datos del formulario
        ##nombre = request.form['nombre']
        ##apellido = request.form['apellido']
        #nombre_completo = f"{nombre} {apellido}"
        ##cedula = request.form['cedula']
        celular = request.form['celular']
        #email = request.form['email']
        genero = request.form['genero']
        nvl_estudio = ','.join(request.form.getlist('nvl_estudio'))  # Convertir a cadena separada por comas
        carrera = ','.join(request.form.getlist('carrera'))  # Convertir a cadena separada por comas
        #imagen_perfil = request.files['imagen_perfil']
        #intereses = request.form.getlist('intereses')
        #otros_intereses = request.form['Otros']

        # Manejar la disponibilidad_c de manera segura
        disponibilidad_c = request.form.get('disponibilidad_c')
        if disponibilidad_c is not None:
            disponibilidad_c = int(disponibilidad_c)
        else:
            # Manejar el caso donde no se proporciona disponibilidad_c
            disponibilidad_c = None  # O el valor por defecto que corresponda

        # Concatenar nombre y apellido para actualizar nombre_completo
        ##nombre_completo = f"{nombre} {apellido}"

        # Manejar la disponibilidad_c de manera segura
        # anios_exp_informatica = request.form.get('anios_exp_informatica')
        # if anios_exp_informatica is not None:
        #     anios_exp_informatica = int(anios_exp_informatica)
        # else:
        #     # Manejar el caso donde no se proporciona disponibilidad_c
        #     anios_exp_informatica = None  # O el valor por defecto que corresponda

        anios_exp_informatica = request.form.get('anios_exp_informatica')

        # Guardar la imagen físicamente en el servidor
        if 'imagen_perfil' in request.files:
            imagen_perfil = request.files['imagen_perfil']
            if imagen_perfil.filename:
                # filename = secure_filename(imagen_perfil.filename)
                # path_to_save = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                # imagen_perfil.save(path_to_save)

                # Generar un nombre único para el archivo
                unique_filename = str(uuid.uuid4()) + "_" + secure_filename(imagen_perfil.filename)
                path_to_save = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                imagen_perfil.save(path_to_save)

                # Actualizar el nombre del archivo de la imagen en la base de datos
                cur = mysql.connection.cursor()
                cur.execute("""
                    UPDATE docente
                    SET imagen_p = %s
                    WHERE id_usuario = %s
                """, (unique_filename, session['user_id']))
                #""", (filename, session['user_id']))
                mysql.connection.commit()
                cur.close()
            #else:
                #flash('No se seleccionó ningún archivo', 'danger')

        #imagen_perfil = request.files['imagen_perfil']

        # Actualizar la base de datos
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE docente
            SET celular = %s,
                genero = %s,
                nvl_estudio = %s,
                carrera = %s,
                disponibilidad_c = %s,
                anios_exp_informatica = %s
            WHERE id_usuario = %s
        """, (celular, genero, nvl_estudio, carrera, disponibilidad_c, anios_exp_informatica, session['user_id']))
        #""", (nombre, apellido, request.form['cedula'], request.form['celular'], request.form['email'], request.form['genero'], ','.join(request.form.getlist('nvl_estudio')), ','.join(request.form.getlist('carrera')), int(request.form['disponibilidad_c']), session['user_id']))
        #""", (nombre, apellido, cedula, celular, email, genero, ','.join(nivel_estudio), ','.join(carrera), disponibilidad, session['user_id']))
        #""", (nombre, apellido, cedula, celular, email, genero, nivel_estudio, carrera, disponibilidad, session['user_id']))
        mysql.connection.commit()
        cur.close()


        # Aquí deberías procesar los datos recibidos, guardarlos en la base de datos, etc.
        # Por simplicidad, aquí solo flashamos un mensaje de éxito
        flash('¡Perfil actualizado correctamente!', 'success')

        # Redirigir de vuelta a la página del perfil (o a donde quieras redirigir después de guardar)
        return redirect(url_for('perfil'))

    flash('Error al actualizar el perfil', 'danger')
    return redirect(url_for('perfil'))

#----------------------------------------------------------------------#

# Ruta para guardar las habilidades del perfil editado
@app.route('/guardar_habilidades_perfil', methods=['POST'])
def guardar_habilidades_perfil():
    if request.method == 'POST':
        #Conexion
        cursor = mysql.connection.cursor()
        # Obtener el ID del usuario recién registrado
        #cursor.execute('SELECT id FROM usuarios WHERE email = %s', (email,))
        #user_id = cursor.fetchone()[0]
        # Obtener el ID del docente recién insertado
        cursor.execute('SELECT id FROM docente WHERE id_usuario = %s', (session['user_id'],))
        id_docente = cursor.fetchone()[0]
        # Obtener id del docente desde la sesión o el formulario, dependiendo de cómo lo manejes
        #id_usuario = session['user_id']  # O como obtengas el id del docente desde la sesión

        # Obtener todas las habilidades técnicas y blandas desde el formulario
        habilidades_tecnicas = {
            'business_intelligence_bi': request.form.get('business_intelligence_bi', type=int),
            'desarrollo_software': request.form.get('desarrollo_software', type=int),
            'analisis_datos': request.form.get('analisis_datos', type=int),
            'gestion_base_datos': request.form.get('gestion_base_datos', type=int),
            'disenio_interfaz': request.form.get('disenio_interfaz', type=int),
            'redes': request.form.get('redes', type=int),
            'sistemas_operativos': request.form.get('sistemas_operativos', type=int),
            'desarrollo_frontend': request.form.get('desarrollo_frontend', type=int),
            'desarrollo_backend': request.form.get('desarrollo_backend', type=int),
            'seguridad_informatica': request.form.get('seguridad_informatica', type=int),
            'gestion_servidores_nube': request.form.get('gestion_servidores_nube', type=int),
            'animacion_grafica': request.form.get('animacion_grafica', type=int),
            'prototipado': request.form.get('prototipado', type=int),
            'criptografia': request.form.get('criptografia', type=int),
            'administracion_servidores': request.form.get('administracion_servidores', type=int),
            'aprendizaje_automatico_machine_learning': request.form.get('aprendizaje_automatico_machine_learning', type=int),
        }

        habilidades_blandas = {
            'comunicacion_asertiva': request.form.get('comunicacion_asertiva', type=int),
            'trabajo_equipo': request.form.get('trabajo_equipo', type=int),
            'resolucion_problemas': request.form.get('resolucion_problemas', type=int),
            'adaptabilidad': request.form.get('adaptabilidad', type=int),
            'empatia': request.form.get('empatia', type=int),
            'tolerancia_estres': request.form.get('tolerancia_estres', type=int),
            'creatividad': request.form.get('creatividad', type=int),
            'liderazgo': request.form.get('liderazgo', type=int),
            'gestion_tiempo': request.form.get('gestion_tiempo', type=int),
            'resiliencia': request.form.get('resiliencia', type=int),
            'pensamiento_critico': request.form.get('pensamiento_critico', type=int),
            'manejo_inteligencia_emocional': request.form.get('manejo_inteligencia_emocional', type=int),
        }

        habilidades_extracurriculares = {
            'manejo_redes_sociales': request.form.get('manejo_redes_sociales', type=int),
            'marketing_digital': request.form.get('marketing_digital', type=int),
            'edicion_video': request.form.get('edicion_video', type=int),
            'idiomas_extranjeros': request.form.get('idiomas_extranjeros', type=int),
            'tecnicas_presentacion': request.form.get('tecnicas_presentacion', type=int),
            'redaccion_creativa': request.form.get('redaccion_creativa', type=int),
            'diseno_grafico': request.form.get('diseno_grafico', type=int),
            'fotografia': request.form.get('fotografia', type=int),
            'animacion_3d': request.form.get('animacion_3d', type=int),
            'negociacion': request.form.get('negociacion', type=int),
            'habilidades_ventas': request.form.get('habilidades_ventas', type=int),
            'mindfulness_meditacion': request.form.get('mindfulness_meditacion', type=int),
        }

        # Obtener intereses seleccionados
        # intereses = request.form.getlist('intereses')
        tipos_intereses = ','.join(request.form.getlist('tipos_intereses'))
        otros = request.form.get('otros', '')  # Obtiene el valor de 'otros', o una cadena vacía si no está presente

        # Actualizar la base de datos con las habilidades técnicas
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE habilidades_t_b
            SET business_intelligence_bi = %s,
                desarrollo_software = %s,
                analisis_datos = %s,
                gestion_base_datos = %s,
                disenio_interfaz = %s,
                redes = %s,
                sistemas_operativos = %s,
                desarrollo_frontend = %s,
                desarrollo_backend = %s,
                seguridad_informatica = %s,
                gestion_servidores_nube = %s,
                animacion_grafica = %s,
                prototipado = %s,
                criptografia = %s,
                administracion_servidores = %s,
                aprendizaje_automatico_machine_learning = %s
            WHERE id_docente = %s
        """, (
            habilidades_tecnicas['business_intelligence_bi'],
            habilidades_tecnicas['desarrollo_software'],
            habilidades_tecnicas['analisis_datos'],
            habilidades_tecnicas['gestion_base_datos'],
            habilidades_tecnicas['disenio_interfaz'],
            habilidades_tecnicas['redes'],
            habilidades_tecnicas['sistemas_operativos'],
            habilidades_tecnicas['desarrollo_frontend'],
            habilidades_tecnicas['desarrollo_backend'],
            habilidades_tecnicas['seguridad_informatica'],
            habilidades_tecnicas['gestion_servidores_nube'],
            habilidades_tecnicas['animacion_grafica'],
            habilidades_tecnicas['prototipado'],
            habilidades_tecnicas['criptografia'],
            habilidades_tecnicas['administracion_servidores'],
            habilidades_tecnicas['aprendizaje_automatico_machine_learning'],
            (id_docente,)
        ))
        mysql.connection.commit()

        # Actualizar la base de datos con las habilidades blandas
        cur.execute("""
            UPDATE habilidades_t_b
            SET comunicacion_asertiva = %s,
                trabajo_equipo = %s,
                resolucion_problemas = %s,
                adaptabilidad = %s,
                empatia = %s,
                tolerancia_estres = %s,
                creatividad = %s,
                liderazgo = %s,
                gestion_tiempo = %s,
                resiliencia = %s,
                pensamiento_critico = %s,
                manejo_inteligencia_emocional = %s
            WHERE id_docente = %s
        """, (
            habilidades_blandas['comunicacion_asertiva'],
            habilidades_blandas['trabajo_equipo'],
            habilidades_blandas['resolucion_problemas'],
            habilidades_blandas['adaptabilidad'],
            habilidades_blandas['empatia'],
            habilidades_blandas['tolerancia_estres'],
            habilidades_blandas['creatividad'],
            habilidades_blandas['liderazgo'],
            habilidades_blandas['gestion_tiempo'],
            habilidades_blandas['resiliencia'],
            habilidades_blandas['pensamiento_critico'],
            habilidades_blandas['manejo_inteligencia_emocional'],
            (id_docente,)
        ))
        mysql.connection.commit()

        # Actualizar la base de datos con las habilidades intereses
        cur.execute("""
            UPDATE habilidades_t_b
            SET manejo_redes_sociales = %s,
                marketing_digital = %s,
                edicion_video = %s,
                idiomas_extranjeros = %s,
                tecnicas_presentacion = %s,
                redaccion_creativa = %s,
                diseno_grafico = %s,
                fotografia = %s,
                animacion_3d = %s,
                negociacion = %s,
                habilidades_ventas = %s,
                mindfulness_meditacion = %s
            WHERE id_docente = %s
        """, (
            habilidades_extracurriculares['manejo_redes_sociales'],
            habilidades_extracurriculares['marketing_digital'],
            habilidades_extracurriculares['edicion_video'],
            habilidades_extracurriculares['idiomas_extranjeros'],
            habilidades_extracurriculares['tecnicas_presentacion'],
            habilidades_extracurriculares['redaccion_creativa'],
            habilidades_extracurriculares['diseno_grafico'],
            habilidades_extracurriculares['fotografia'],
            habilidades_extracurriculares['animacion_3d'],
            habilidades_extracurriculares['negociacion'],
            habilidades_extracurriculares['habilidades_ventas'],
            habilidades_extracurriculares['mindfulness_meditacion'],
            (id_docente,)
        ))
        mysql.connection.commit()
        
        # Actualizar la base de datos
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE intereses
            SET tipos_intereses = %s,
                otros = %s
            WHERE id_docente = %s
        """, (tipos_intereses, otros, id_docente))
        mysql.connection.commit()
        cur.close()

        # if result:
        #     tipos_intereses = result[0]
        #     # Dividir la cadena en una lista de intereses
        #     intereses = tipos_intereses.split(',')
        # else:
        #     intereses = []

        # # Obtener el ID de habilidades_t_b recién actualizado
        # cur.execute('SELECT id FROM habilidades_t_b WHERE id_docente = %s', (id_docente,))
        # habilidades_t_b_id = cur.fetchone()[0]

        # # Actualizar la tabla resultados_difusos_h_t con los resultados difusos
        # cur.execute("""
        #     UPDATE resultados_difusos_h_t
        #     SET resultado_difuso = %s,
        #         resultado_difuso_g = %s,
        #         resultado_difuso_d = %s,
        #         resultado_difuso_s = %s,
        #         resultado_difuso_i = %s
        #     WHERE id_habilidades_t_b = %s
        # """, (
        #     request.form.get('resultado_difuso', type=float),
        #     request.form.get('resultado_difuso_g', type=float),
        #     request.form.get('resultado_difuso_d', type=float),
        #     request.form.get('resultado_difuso_s', type=float),
        #     request.form.get('resultado_difuso_i', type=float),
        #     (habilidades_t_b_id)
        # ))

        # Agregar impresión de valores para debugging
        # resultado_difuso = request.form.get('resultado_difuso', type=float)
        # resultado_difuso_g = request.form.get('resultado_difuso_g', type=float)
        # resultado_difuso_d = request.form.get('resultado_difuso_d', type=float)
        # resultado_difuso_s = request.form.get('resultado_difuso_s', type=float)
        # resultado_difuso_i = request.form.get('resultado_difuso_i', type=float)

        # print(f"Valor de resultado_difuso: {resultado_difuso}")
        # print(f"Valor de resultado_difuso_g: {resultado_difuso_g}")
        # print(f"Valor de resultado_difuso_d: {resultado_difuso_d}")
        # print(f"Valor de resultado_difuso_s: {resultado_difuso_s}")
        # print(f"Valor de resultado_difuso_i: {resultado_difuso_i}")

        # Ejecutar el commit para aplicar los cambios en la base de datos
        #mysql.connection.commit()

        #mysql.connection.commit()
        #cur.close()

        # Flash de éxito y redirección a la página del perfil
        flash('¡Habilidades actualizadas correctamente!', 'success')
        return redirect(url_for('perfil'))

    flash('Error al actualizar las habilidades', 'danger')
    return redirect(url_for('perfil'))


# Definición de la función para clasificar habilidades
def classify_skill(value):
    if value is None:
        return ('Desconozco', 'text-placeholder')
        #return ('Desconozco', 'text-placeholder text-minimo')
    elif value < 10:
        return ('Desconozco', 'text-placeholder')
        #return ('Desconozco', 'text-placeholder text-minimo')
    elif value < 50:
        return ('Principiante', 'text-placeholder')
        #return ('Principiante', 'text-placeholder text-bajo')
    elif value < 75:
        return ('Intermedio', 'text-placeholder')
        #return ('Intermedio', 'text-placeholder text-medio')
    elif value < 90:
        return ('Avanzado', 'text-placeholder')
        #return ('Avanzado', 'text-placeholder text-alto')
    else:
        return ('Experto', 'text-placeholder')
        #return ('Experto', 'text-placeholder text-maximo', 'triangle triangle-maximo')

# Registrar la función en el entorno de Jinja2
app.jinja_env.globals.update(classify_skill=classify_skill)



# @app.route('/resultado_difuso', methods=['POST'])
# def resultado_difuso():
#     global resultado_difuso_global

#     if request.method == 'POST':
#         resultado_difuso_global = request.form.get('resultado_difuso', type=float)

#         flash('¡Resultado difuso actualizado correctamente!', 'success')

#         return redirect(url_for('perfil'))  # Redireccionar a la página de perfil o donde sea adecuado

#     flash('Error al actualizar el resultado difuso', 'danger')
#     return redirect(url_for('perfil'))  # Redireccionar a la página de perfil o donde sea adecuado


#@app.route('/perfil')
#def mostrar_perfil():
#    global resultado_difuso_global  # Acceder al resultado difuso global

    # Aquí puedes pasar otros datos necesarios para el perfil si es necesario
#    contexto = {
#        'resultado_difuso': resultado_difuso_global
#    }

#    return render_template('perfil.html', **contexto)

#@app.route('/download_excel/<int:docente_id>', methods=['POST'])
# @app.route('/download_excel', methods=['POST'])
# def download_excel():
#     if request.method == 'POST':
#     # Recuperar datos del formulario
#     #docente_nombre_apellido = request.form.get('docente_nombre_apellido')
#         docente_id = request.form.get('docente_id')

#         # Verificar que docente esté definido en el contexto actual
#         #docente = request.form.get('docente')  # Ejemplo: Recuperar docente del formulario

#         # Realizar consulta a la base de datos para obtener datos del docente
#         cursor = mysql.connection.cursor()
#         cursor.execute("""
#             SELECT 
#                 d.nombre,
#                 d.apellido,
#                 d.cedula,
#                 d.celular,
#                 d.email,
#                 d.genero,
#                 d.nvl_estudio,
#                 d.carrera,
#                 d.disponibilidad_c,
#                 rd.resultado_difuso,
#                 rd.resultado_difuso_g,
#                 rd.resultado_difuso_d,
#                 rd.resultado_difuso_s,
#                 rd.resultado_difuso_i
#             FROM 
#                 habilidades_t_b h
#             JOIN 
#                 docente d ON h.id_docente = d.id
#             JOIN 
#                 resultados_difusos_h_t rd ON rd.id_habilidades_t_b = h.id
#             WHERE 
#                 d.id = %s;
#         """, (docente_id,))
#         docente_data = cursor.fetchone()
#         cursor.close()

#         # Crear un libro de Excel y una hoja
#         # wb = Workbook()
#         # ws = wb.active
#         # ws.title = 'Resultados de Búsqueda'

#         # Agregar encabezados a la hoja
#         # headers = ['Foto', 'Nombre y Apellido', 'Cédula', 'Celular', 'Email', 'Género', 'Nivel de Estudio', 'Carrera', 'Disponibilidad', 'Resultado Difuso del Docente', 'Porcentaje de Similitud', 'Nivel de Confianza']
#         # ws.append(headers)

#         # Obtener datos del docente y añadir a la hoja
#         if docente_data:
#             # Crear libro de Excel y hoja
#             wb = Workbook()
#             ws = wb.active
#             ws.title = 'Resultados de Búsqueda'

#             # Agregar encabezados
#             #headers = ['Foto', 'Nombre y Apellido', 'Cédula', 'Celular', 'Email', 'Género', 'Nivel de Estudio', 'Carrera', 'Disponibilidad', 'Resultado Difuso', 'Resultado Difuso G', 'Resultado Difuso D', 'Resultado Difuso S', 'Resultado Difuso I']
#             headers = ['Nombre', 'Apellido', 'Cédula', 'Celular', 'Email', 'Género', 'Nivel de Estudio', 'Carrera', 'Disponibilidad', 'Resultado Difuso', 'Resultado Difuso G', 'Resultado Difuso D', 'Resultado Difuso S', 'Resultado Difuso I']
#             ws.append(headers)

#             # Preparar datos del docente y resultados difusos
#             row_data = [
#                 #'',  # Lógica para la imagen si es necesaria
#                 #f"{docente_data[0]} {docente_data[1]}",
#                 docente_data[0],
#                 docente_data[1],
#                 docente_data[2],
#                 docente_data[3],
#                 docente_data[4],
#                 docente_data[5],
#                 docente_data[6],
#                 docente_data[7],
#                 docente_data[8],
#                 docente_data[9],    # resultado_difuso
#                 docente_data[10],   # resultado_difuso_g
#                 docente_data[11],   # resultado_difuso_d
#                 docente_data[12],   # resultado_difuso_s
#                 docente_data[13]    # resultado_difuso_i
#             ]
#             ws.append(row_data)

#             # Guardar el libro de Excel
#             excel_filename = f'Resultados_Busqueda_{docente_id}.xlsx'
#             wb.save(excel_filename)

#             # Ofrecer el archivo Excel para descargar
#             return send_file(excel_filename, as_attachment=True)

#         else:
#             # Manejar caso donde docente no está definido
#             return "Error: No se encontró información del docente para generar el archivo Excel."
#     return redirect(url_for('busqueda_inteligente'))  # Ejemplo de redirección a la página principal

@app.context_processor
def inject_user():
    if 'logged_in' in session:
        #cursor = mysql.connection.cursor()
        #cursor.execute('SELECT nombre_completo FROM usuarios WHERE id = %s', (session['user_id'],))
        #user = cursor.fetchone()
        #cursor.close()
        #if user:
        #    return {'nombre_completo': user[0]}
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT nombre, apellido, email FROM docente WHERE id_usuario = %s', (session['user_id'],))
        user = cursor.fetchone()
        cursor.close()
        if user:
            return {'nombre': user[0], 'apellido': user[1], 'email': user[2]}
    return {}



#@app.route('/favicon.ico')
#def favicon():
#    return app.send_static_file('favicon.ico')


# Ejecuta la aplicación
if __name__ == "__main__":
    app.run(debug=True)
    #app.run(port=3000, debug=True)