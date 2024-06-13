# main.py
from app import app
from db import init_connection, mysql
from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from docentes import docentes_bp
from ontologia_fuzzy import OntologiaFuzzy

# Inicializa la configuración de MySQL
init_connection(app)

# Registra el Blueprint de docentes
app.register_blueprint(docentes_bp)

#Settings jjjjjj
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

@app.route('/')
def home():
    if 'logged_in' in session:
        return redirect(url_for('index'))
    return render_template('ini.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE email = %s', (email,))
    user = cursor.fetchone()
    if user and check_password_hash(user[4], password):  # user[4] is the password field
        session['logged_in'] = True
        session['user_id'] = user[0]  # user[0] is the user ID field
        session['username'] = user[3]  # user[3] is the username field
        flash('Has iniciado sesión correctamente', 'success')
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
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE email = %s', (email,))
    existing_user = cursor.fetchone()
    if existing_user:
        flash('El correo electrónico ya está registrado', 'danger')
        return redirect(url_for('home'))
    hashed_password = generate_password_hash(password)
    cursor.execute('INSERT INTO usuarios (nombre_completo, email, usuario, password) VALUES (%s, %s, %s, %s)',
                   (name, email, username, hashed_password))
    mysql.connection.commit()
    flash('Registro exitoso, ahora puedes iniciar sesión', 'success')
    return redirect(url_for('home'))

@app.route('/index')
def index():
    if not session.get('logged_in'):
        flash('Por favor, inicia sesión para acceder a esta página', 'danger')
        return redirect(url_for('home'))
    return render_template('index.html')

@app.route('/logout', methods=['GET', 'POST'] )
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('home'))

@app.route('/perfil')
def perfil():
    # Tu lógica para la vista 'register' aquí
    return render_template('perfil.html')

@app.route('/register')
def register():
    # Tu lógica para la vista 'register' aquí
    return render_template('register.html')

@app.route('/busqueda_inteligente', methods=['GET', 'POST'])
def busqueda_inteligente():
    if request.method == 'POST':
        # Maneja la lógica de la búsqueda aquí
        pass
    return render_template('busqueda_inteligente.html')

# Ejecuta la aplicación
if __name__ == "__main__":
    app.run(debug=True)
    #app.run(port=3000, debug=True)