#Routes are defined here
from flask import url_for
from main import app


@app.route('/')
def home():
    return "Hello world"