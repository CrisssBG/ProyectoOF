#app.py
from flask import Flask

# Application initializations
# app = Flask (__name__)
app = Flask(__name__, template_folder='.')

#Settings
app.secret_key = 'mysecretkey'

