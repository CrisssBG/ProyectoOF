#db.py
#import mysql.connector
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv  # Importa la función load_dotenv
import os

# Llama a load_dotenv() para cargar las variables de entorno desde el archivo .env
load_dotenv()

# Inicializa una instancia global de MySQL
# mysql = MySQL()    
# Inicializa una instancia global de SQLAlchemy
db = SQLAlchemy()

#MySQL Connection
def init_connection(app):
    # Mysql Settings
    ##app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
    ##app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
    ##app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
    ##app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
    #app.config['MYSQL_CURSORCLASS'] = 'DictCursor' #No me deja mostrar datos
    ##mysql.init_app(app) # Inicializa la instancia MySQL con la aplicación Flask
    #mysql = MySQL(app) # MySQL Connection
    #return mysql
    #return {'app': app, 'mysql': mysql}
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mssql+pyodbc://{os.getenv('SQL_SERVER_USER')}:{os.getenv('SQL_SERVER_PASSWORD')}@"
        f"{os.getenv('SQL_SERVER_HOST')}/{os.getenv('SQL_SERVER_DB')}?driver=ODBC+Driver+17+for+SQL+Server"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)