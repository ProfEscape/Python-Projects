from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'password'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///site.db' 
db = SQLAlchemy(app)

from main import models

# Ensure tables are created when the app runs
with app.app_context():
    db.create_all()

from main import routes