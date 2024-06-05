#app.py
from flask import Flask

# Application initializations
app = Flask (__name__)

#Settings
app.secret_key = 'mysecretkey'
