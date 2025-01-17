from flask import render_template, redirect, url_for, flash, request, session
from werkzeug.security import check_password_hash,generate_password_hash
from main import app, db
from main.models import Student, Teacher, Subject
from main.forms import SignUpForm, LoginForm

@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html", title="Home")

@app.route('/dashboard-student')
def dashboard_student():
    user_id = session.get('user_id')
    if session.get('user_role') != 'student' or not user_id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    student = Student.query.get(user_id)
    return render_template("student_dashboard.html", title="Student Dashboard", student=student)

@app.route('/dashboard-teacher')
def dashboard_teacher():
    user_id = session.get('user_id')
    if session.get('user_role') != 'teacher' or not user_id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    teacher = Teacher.query.get(user_id)
    return render_template("teacher_dashboard.html", title="Teacher Dashboard", teacher=teacher)


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        # Determine the role and create the appropriate user
        if form.role.data == 'student':
            user = Student(name=form.username.data, email=form.email.data, usn=form.usn.data, password= form.password.data)
        elif form.role.data == 'teacher':
            user = Teacher(name=form.username.data, email=form.email.data, teacher_id=form.teacher_id.data, password= form.password.data)
        else:
            flash("Invalid role selected", 'danger')
            return redirect(url_for('sign_up'))

        # Add user to the database
        try:
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('An error occurred while creating your account.', 'danger')
            print(e)
    return render_template("signup.html", title="Sign Up", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Check if the user is a student
        student = Student.query.filter_by(email=email).first()
        # print('\nHashed Password:')
        # print(student.password, password)

        if student:
            session['user_id'] = student.id
            session['user_role'] = 'student'
            flash('Logged in successfully as a student!', 'success')
            return redirect(url_for('dashboard_student'))
        else:
            flash('Logged in not successfull as a student!', 'success')

        # Check if the user is a teacher
        teacher = Teacher.query.filter_by(email=email).first()
        if teacher and check_password_hash(teacher.password, password):
            session['user_id'] = teacher.id
            session['user_role'] = 'teacher'
            flash('Logged in successfully as a teacher!', 'success')
            return redirect(url_for('teacher_dashboard'))

    else:
        print(form.errors)  # Print validation errors for debugging
        flash('Form validation failed.', 'danger')

    return render_template("login.html", title="Login", form=form)
    


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         email = form.email.data
#         password = form.password.data

#         # Check if the user is a student
#         student = Student.query.filter_by(email=email).first()
#         if student and check_password_hash(student.password, password):
#             session['user_id'] = student.id
#             session['user_role'] = 'student'
#             flash('Logged in successfully!', 'success')
#             return redirect(url_for('dashboard_student'))

#         # Check if the user is a teacher
#         teacher = Teacher.query.filter_by(email=email).first()
#         if teacher and check_password_hash(teacher.password, password):
#             session['user_id'] = teacher.id
#             session['user_role'] = 'teacher'
#             flash('Logged in successfully!', 'success')
#             return redirect(url_for('dashboard_teacher'))

#         flash('Invalid email or password', 'danger')
#     return render_template("login.html", title="Login", form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


@app.route('/check-database')
def check_database():
    # Fetch all students
    students = Student.query.all()

    # Fetch all teachers
    teachers = Teacher.query.all()

    # Render a template to display the data
    return render_template("check_database.html", students=students, teachers=teachers)



@app.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    if 'user_id' not in session or session.get('user_role') != 'student':
        flash('You must be logged in as a student to access this page.', 'danger')
        return redirect(url_for('login'))

    student_id = session['user_id']

    if request.method == 'POST':
        subject_name = request.form.get('subject_name')
        subject_code = request.form.get('subject_code')

        if not subject_name or not subject_code:
            flash('Subject name and code cannot be empty.', 'danger')
            return redirect(url_for('add_subject'))

        # Check if the subject already exists for the student
        existing_subject = Subject.query.filter_by(name=subject_name, student_id=student_id).first()
        if existing_subject:
            flash('Subject already exists.', 'warning')
            return redirect(url_for('add_subject'))

        # Add the new subject (teacher_id can be None or a specific value)
        new_subject = Subject(
            name=subject_name, 
            code=subject_code, 
            student_id=student_id, 
            teacher_id=None  # Adjust if you have a specific teacher
        )
        db.session.add(new_subject)
        db.session.commit()
        flash('Subject added successfully!', 'success')
        return redirect(url_for('add_subject'))

    # Fetch existing subjects for the logged-in student
    subjects = Subject.query.filter_by(student_id=student_id).all()
    return render_template('add_subject.html', title='Add Subject', subjects=subjects)

# @app.route('/add_subject', methods=['GET', 'POST'])
# def add_subject():
#     if 'user_id' not in session or session.get('user_role') != 'student':
#         flash('You must be logged in as a student to access this page.', 'danger')
#         return redirect(url_for('login'))

#     student_id = session['user_id']

#     if request.method == 'POST':
#         subject_name = request.form.get('subject_name')
#         if not subject_name:
#             flash('Subject name cannot be empty.', 'danger')
#             return redirect(url_for('add_subject'))

#         # Check if the subject already exists for the student
#         existing_subject = Subject.query.filter_by(name=subject_name, student_id=student_id).first()
#         if existing_subject:
#             flash('Subject already exists.', 'warning')
#             return redirect(url_for('add_subject'))

#         # Add the new subject
#         new_subject = Subject(name=subject_name, student_id=student_id)
#         db.session.add(new_subject)
#         db.session.commit()
#         flash('Subject added successfully!', 'success')
#         return redirect(url_for('add_subject'))

#     # Fetch existing subjects
#     subjects = Subject.query.filter_by(student_id=student_id).all()
#     return render_template('add_subject.html', title='Add Subject', subjects=subjects)

