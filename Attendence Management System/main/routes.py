from main import app
from flask import render_template



@app.route('/')
def home():
    return render_template("home.html", title="Home")


@app.route('/dashboard-Teacher')
def dashboardTeacher():
    return render_template("teacher_dashboard.html", title="Dashboard")


@app.route('/dashboard-Student')
def dashboardStudent():
    return render_template("student_dashboard.html", title="Dashboard")


@app.route('/login')
def login():
    return render_template("login.html", title="Login")

@app.route('/signup')
def signUp():
    return render_template("signup.html", title="Sign up")