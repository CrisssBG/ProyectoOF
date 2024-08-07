#models.py
from db import db
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    usuario = db.Column(db.String(255))
    password = db.Column(db.String(255))

    # Relaciones
    docentes = db.relationship('Docente', backref='usuario', lazy=True)

class Docente(db.Model):
    __tablename__ = 'docente'

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    nombre = db.Column(db.String(255))
    apellido = db.Column(db.String(255))
    cedula = db.Column(db.String(50), unique=True)
    celular = db.Column(db.String(50))
    email = db.Column(db.String(255))
    genero = db.Column(db.String(50), check=db.CheckConstraint(genero.in_(['Masculino', 'Femenino', 'Otro'])))
    nvl_estudio = db.Column(db.String(255))
    carrera = db.Column(db.String(255))
    imagen_p = db.Column(db.String(255))
    disponibilidad_c = db.Column(db.Integer)
    anios_exp_informatica = db.Column(db.Integer)

    # Relaciones
    habilidades_t_b = db.relationship('HabilidadesTB', backref='docente', lazy=True)
    intereses = db.relationship('Intereses', backref='docente', lazy=True)

class HabilidadesTB(db.Model):
    __tablename__ = 'habilidades_t_b'

    id = db.Column(db.Integer, primary_key=True)
    id_docente = db.Column(db.Integer, db.ForeignKey('docente.id'), nullable=False)
    desarrollo_software = db.Column(db.Integer, nullable=True)
    diseno_grafico = db.Column(db.Integer, nullable=True)
    comunicacion_asertiva = db.Column(db.Integer, nullable=True)
    analisis_datos = db.Column(db.Integer, nullable=True)

    # Relaciones
    resultados_difusos_h_t = db.relationship('ResultadosDifusosHT', backref='habilidades_t_b', lazy=True)

class ResultadosDifusosHT(db.Model):
    __tablename__ = 'resultados_difusos_h_t'

    id = db.Column(db.Integer, primary_key=True)
    id_habilidades_t_b = db.Column(db.Integer, db.ForeignKey('habilidades_t_b.id'), nullable=False)
    resultado_difuso = db.Column(db.Float, nullable=True)
    resultado_difuso_g = db.Column(db.Float, nullable=True)
    resultado_difuso_d = db.Column(db.Float, nullable=True)
    resultado_difuso_s = db.Column(db.Float, nullable=True)
    resultado_difuso_i = db.Column(db.Float, nullable=True)
    resultado_difuso_bhl = db.Column(db.Float, nullable=True)
    resultado_difuso_bhc = db.Column(db.Float, nullable=True)
    resultado_difuso_bhi = db.Column(db.Float, nullable=True)
    resultado_difuso_bhm = db.Column(db.Float, nullable=True)
    resultado_difuso_ecd = db.Column(db.Float, nullable=True)
    resultado_difuso_eec = db.Column(db.Float, nullable=True)
    resultado_difuso_edp = db.Column(db.Float, nullable=True)
    resultado_difuso_eit = db.Column(db.Float, nullable=True)

class Intereses(db.Model):
    __tablename__ = 'intereses'

    id = db.Column(db.Integer, primary_key=True)
    id_docente = db.Column(db.Integer, db.ForeignKey('docente.id'), nullable=False)
    tipos_intereses = db.Column(db.String(255), nullable=True)
    otros = db.Column(db.String(255), nullable=True)

# class Usuario(db.Model):
#     __tablename__ = 'usuarios'
    
#     id = db.Column(db.Integer, primary_key=True)
#     nombre_completo = db.Column(db.String(255))
#     email = db.Column(db.String(255), unique=True)
#     usuario = db.Column(db.String(255))
#     password = db.Column(db.String(255))

# class Docente(db.Model):
#     __tablename__ = 'docente'
    
#     id = db.Column(db.Integer, primary_key=True)
#     id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
#     nombre = db.Column(db.String(255))
#     apellido = db.Column(db.String(255))
#     cedula = db.Column(db.String(50))
#     email = db.Column(db.String(255))
#     imagen_p = db.Column(db.String(255))

# class HabilidadesTB(db.Model):
#     __tablename__ = 'habilidades_t_b'
    
#     id = db.Column(db.Integer, primary_key=True)
#     id_docente = db.Column(db.Integer, db.ForeignKey('docente.id'))
#     desarrollo_software = db.Column(db.Integer)
#     diseno_grafico = db.Column(db.Integer)
#     comunicacion_asertiva = db.Column(db.Integer)
#     analisis_datos = db.Column(db.Integer)

# class ResultadosDifusosHT(db.Model):
#     __tablename__ = 'resultados_difusos_h_t'
    
#     id = db.Column(db.Integer, primary_key=True)
#     id_habilidades_t_b = db.Column(db.Integer, db.ForeignKey('habilidades_t_b.id'))
#     desarrollo_software = db.Column(db.Float)
#     redes = db.Column(db.Float)
#     analisis_datos = db.Column(db.Float)

# class Intereses(db.Model):
#     __tablename__ = 'intereses'
    
#     id = db.Column(db.Integer, primary_key=True)
#     id_docente = db.Column(db.Integer, db.ForeignKey('docente.id'))
#     tipos_intereses = db.Column(db.String(255))
#     otros = db.Column(db.String(255))

    





    