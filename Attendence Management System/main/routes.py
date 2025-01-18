from flask import render_template, redirect, url_for, flash, request, session
from main import app, db
from main.models import Student, Teacher, Subject, Attendance
from main.forms import SignUpForm, LoginForm, TeacherSignUpForm, SubjectForm
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html", title="Home")


@app.route('/dashboard-student')
def dashboard_student():
    if 'user_id' not in session or session.get('user_role') != 'student':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

    student_id = session['user_id']
    student = Student.query.get(student_id)
    
    # Get attendance statistics for each subject
    subjects_data = []
    for subject in student.subjects:
        total_classes = subject.total_classes()
        attended_classes = len([
            att for att in subject.attendance_records 
            if att.student_id == student_id and att.status
        ])
        
        subjects_data.append({
            'id': subject.id,
            'name': subject.name,
            'code': subject.code,
            'total': total_classes,
            'attended': attended_classes,
            'attendance_enabled': subject.attendance_enabled,
            'already_marked_today': Attendance.query.filter_by(
                student_id=student_id,
                subject_id=subject.id,
                date=date.today()
            ).first() is not None
        })

    return render_template(
        "student_dashboard.html",
        title="Student Dashboard",
        student=student,
        subjects=subjects_data
    )



# In routes.py
@app.route('/dashboard-teacher')
def dashboard_teacher():
    if 'user_id' not in session or session.get('user_role') != 'teacher':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

    teacher = Teacher.query.get(session['user_id'])
    return render_template(
        "teacher_dashboard.html",
        title="Teacher Dashboard",
        teacher=teacher,
        subjects=teacher.subjects  # Pass the teacher's subjects
    )


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = Student(
            name=form.username.data,
            email=form.email.data,
            usn=form.usn.data,
            password=hashed_password
        )
        try:
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating your account.', 'danger')
            print(e)
    return render_template("signup.html", title="Sign Up", form=form)


@app.route('/teacher_signup', methods=['GET', 'POST'])
def teacher_signup():
    form = TeacherSignUpForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = Teacher(
            name=form.username.data,
            email=form.email.data,
            teacher_id=form.teacher_id.data,
            password=hashed_password
        )

        # Add subjects for the teacher
        for subject_form in form.subjects.entries:
            subject = Subject(
                name=subject_form.subject_name.data,
                code=subject_form.subject_code.data,
                teacher=user
            )
            db.session.add(subject)

        try:
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating your account.', 'danger')
            print(e)

    return render_template("teacher_signup.html", title="Teacher Sign Up", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        student = Student.query.filter_by(email=email).first()
        if student and check_password_hash(student.password, password):
            session['user_id'] = student.id
            session['user_role'] = 'student'
            flash('Logged in successfully as a student!', 'success')
            return redirect(url_for('dashboard_student'))

        teacher = Teacher.query.filter_by(email=email).first()
        if teacher and check_password_hash(teacher.password, password):
            session['user_id'] = teacher.id
            session['user_role'] = 'teacher'
            flash('Logged in successfully as a teacher!', 'success')
            return redirect(url_for('dashboard_teacher'))

        flash('Invalid email or password.', 'danger')

    return render_template("login.html", title="Login", form=form)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


# In routes.py
@app.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    if 'user_id' not in session or session.get('user_role') != 'student':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

    form = SubjectForm()
    student = Student.query.get(session['user_id'])

    if form.validate_on_submit():
        subject_code = form.subject_code.data.strip()
        subject_name = form.subject_name.data.strip()

        # Check if subject already exists
        existing_subject = Subject.query.filter_by(code=subject_code).first()

        if existing_subject:
            if existing_subject in student.subjects:
                flash('You have already enrolled in this subject.', 'warning')
            else:
                student.subjects.append(existing_subject)
                db.session.commit()
                flash(f'Successfully enrolled in {existing_subject.name}!', 'success')
                return redirect(url_for('dashboard_student'))
        else:
            flash('Subject not found. Please enter a valid subject code.', 'danger')

    # Get all available subjects (subjects that the student hasn't enrolled in yet)
    available_subjects = Subject.query.filter(
        ~Subject.students.any(Student.id == student.id)
    ).all()

    return render_template(
        'add_subject.html',
        title='Add Subject',
        form=form,
        available_subjects=available_subjects,
        current_subjects=student.subjects
    )


# @app.route('/add_subject', methods=['GET', 'POST'])
# def add_subject():
#     form = SubjectForm()
#     if 'user_id' not in session or session.get('user_role') != 'student':
#         flash('Unauthorized access!', 'danger')
#         return redirect(url_for('login'))

#     student_id = session['user_id']
#     student = Student.query.get(student_id)

#     if request.method == 'POST':
#         subject_code = request.form.get('subject_code').strip()
#         subject_name = request.form.get('subject_name').strip()

#         if not subject_code or not subject_name:
#             flash('Both subject code and name are required.', 'danger')
#             return redirect(url_for('add_subject'))

#         # Check if subject already exists
#         subject = Subject.query.filter_by(code=subject_code).first()

#         if subject:
#             if subject in student.subjects:
#                 flash('You have already added this subject.', 'warning')
#                 return redirect(url_for('add_subject'))
#         else:
#             # Create a new subject if it doesn't exist
#             subject = Subject(name=subject_name, code=subject_code)
#             db.session.add(subject)
#             db.session.commit()

#         # Add subject to student's subjects
#         student.subjects.append(subject)
#         db.session.commit()
#         flash(f'Subject "{subject.name}" added successfully!', 'success')
#         return redirect(url_for('dashboard_student'))

#     available_subjects = Subject.query.filter(~Subject.students.any(id=student_id)).all()

#     return render_template(
#         'add_subject.html',
#         title='Add Subject',
#         form = form,
#         subjects=available_subjects
#     )


@app.route('/toggle_attendance/<int:subject_id>', methods=['POST'])
def toggle_attendance(subject_id):
    if session.get('user_role') != 'teacher':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    
    subject = Subject.query.get(subject_id)
    if not subject:
        flash('Subject not found.', 'danger')
        return redirect(url_for('dashboard_teacher'))
    
    # Toggle attendance status
    subject.attendance_enabled = not subject.attendance_enabled
    db.session.commit()
    status = "enabled" if subject.attendance_enabled else "disabled"
    flash(f'Attendance for "{subject.name}" has been {status}.', 'success')
    return redirect(url_for('dashboard_teacher'))


# In routes.py


@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    if session.get('user_role') != 'student':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

    subject_id = request.form.get('subject_id')
    student_id = session.get('user_id')
    
    subject = Subject.query.get(subject_id)
    student = Student.query.get(student_id)

    if not subject or subject not in student.subjects:
        flash('Invalid subject selection.', 'danger')
        return redirect(url_for('dashboard_student'))

    if not subject.attendance_enabled:
        flash('Attendance is not enabled for this subject.', 'danger')
        return redirect(url_for('dashboard_student'))

    # Check if attendance already marked for today
    existing_attendance = Attendance.query.filter_by(
        student_id=student_id,
        subject_id=subject_id,
        date=date.today()
    ).first()

    if existing_attendance:
        flash('Attendance already marked for today.', 'warning')
        return redirect(url_for('dashboard_student'))

    # Create new attendance record
    attendance = Attendance(
        student_id=student_id,
        subject_id=subject_id,
        date=date.today(),
        status=True
    )

    try:
        db.session.add(attendance)
        db.session.commit()
        flash(f'Attendance marked for {subject.name}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error marking attendance.', 'danger')
        print(e)

    return redirect(url_for('dashboard_student'))


@app.route('/check-database')
def check_database():
    # Fetch all students
    students = Student.query.all()

    # Fetch all teachers
    teachers = Teacher.query.all()

    #Fetch all the subjects
    subjects = Subject.query.all()

    # Render a template to display the data
    return render_template("check_database.html", students=students, teachers=teachers, subjects=subjects)












# from flask import render_template, redirect, url_for, flash, request, session
# from werkzeug.security import check_password_hash, generate_password_hash
# from main import app, db
# from main.models import Student, Teacher, Subject
# from main.forms import SignUpForm, LoginForm, TeacherSignUpForm, SubjectForm

# @app.route('/')
# @app.route('/home')
# def home():
#     return render_template("home.html", title="Home")

# @app.route('/dashboard-student')
# def dashboard_student():
#     user_id = session.get('user_id')
#     if session.get('user_role') != 'student' or not user_id:
#         flash('Unauthorized access!', 'danger')
#         return redirect(url_for('login'))
#     student = Student.query.get(user_id)
#     return render_template("student_dashboard.html", title="Student Dashboard", student=student)

# @app.route('/dashboard-teacher')
# def dashboard_teacher():
#     user_id = session.get('user_id')
#     if session.get('user_role') != 'teacher' or not user_id:
#         flash('Unauthorized access!', 'danger')
#         return redirect(url_for('login'))
#     teacher = Teacher.query.get(user_id)
#     return render_template("teacher_dashboard.html", title="Teacher Dashboard", teacher=teacher)


# @app.route('/signup', methods=['GET', 'POST'])
# def sign_up():
#     form = SignUpForm()
#     if form.validate_on_submit():
        
#         user = Student(
#             name=form.username.data, 
#             email=form.email.data, 
#             usn=form.usn.data, 
#             password= form.password.data
#         )
        

#         # Add user to the database
#         try:
#             db.session.add(user)
#             db.session.commit()
#             flash('Account created successfully!', 'success')
#             return redirect(url_for('login'))
#         except Exception as e:
#             flash('An error occurred while creating your account.', 'danger')
#             print(e)
#     return render_template("signup.html", title="Sign Up", form=form)


# @app.route('/teacher_signup', methods=['GET', 'POST'])
# def teacher_signup():
#     form = TeacherSignUpForm()
#     print("Form validate_on_submit():", form.validate_on_submit())
#     print("Form data received:", form.data)
    
#     if form.validate_on_submit():
#         user = Teacher(
#             name=form.username.data,
#             email=form.email.data,
#             teacher_id=form.teacher_id.data,
#             password=form.password.data
#         )

#         # Add subjects for the teacher
#         for subject_form in form.subjects.entries:
#             subject = Subject(
#                 name=subject_form.data['subject_name'],
#                 code=subject_form.data['subject_code'],
#                 student_id= None,
#                 teacher=user
#             )
#             db.session.add(subject)
        
#         # Add the user to the database
#         try:
#             db.session.add(user)
#             db.session.commit()
#             flash('Account created successfully!', 'success')
#             return redirect(url_for('login'))
#         except Exception as e:
#             db.session.rollback()
#             flash('An error occurred while creating your account.', 'danger')
#             print(e)
#     else:
#         print("Form errors:", form.errors)
#         flash('Please correct the errors in the form.', 'danger')

#     return render_template("teacher_signup.html", title="Teacher Sign Up", form=form)






# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     print(form.validate_on_submit())
#     if form.validate_on_submit():
#         email = form.email.data
#         password = form.password.data

#         # Check if the user is a student
#         student = Student.query.filter_by(email=email).first()
#         # print('\nHashed Password:')
#         # print(student.password, password)

#         if student and password == student.password:
#             session['user_id'] = student.id
#             session['user_role'] = 'student'
#             flash('Logged in successfully as a student!', 'success')
#             return redirect(url_for('dashboard_student'))
#         else:
#             print("Login credentials didn't match")
#             flash('Logged in not successfull as a student!', 'success')

#         # Check if the user is a teacher
#         teacher = Teacher.query.filter_by(email=email).first()
#         if teacher and password == teacher.password:                   #and check_password_hash(teacher.password, password):
#             session['user_id'] = teacher.id
#             session['user_role'] = 'teacher'
#             flash('Logged in successfully as a teacher!', 'success')
#             return redirect(url_for('dashboard_teacher'))
#         print("Login credentials didn't match")
#     else:
#         print(form.errors)  # Print validation errors for debugging
#         flash('Form validation failed.', 'danger')

#     return render_template("login.html", title="Login", form=form)
    


# @app.route('/logout')
# def logout():
#     session.clear()
#     flash('You have been logged out.', 'success')
#     return redirect(url_for('home'))


# @app.route('/check-database')
# def check_database():
#     # Fetch all students
#     students = Student.query.all()

#     # Fetch all teachers
#     teachers = Teacher.query.all()

#     #Fetch all the subjects
#     subjects = Subject.query.all()

#     # Render a template to display the data
#     return render_template("check_database.html", students=students, teachers=teachers, subjects=subjects)



# @app.route('/add_subject', methods=['GET', 'POST'])
# def add_subject():
#     form = SubjectForm()
#     if 'user_id' not in session or session.get('user_role') != 'student':
#         flash('You must be logged in as a student to access this page.', 'danger')
#         return redirect(url_for('login'))

#     student_id = session['user_id']
#     student = Student.query.get(student_id)

#     if request.method == 'POST':
#         subject_id = request.form.get('subject_id')

#         # Validate input
#         if not subject_id:
#             flash('Subject selection is required.', 'danger')
#             return redirect(url_for('add_subject'))

#         subject = Subject.query.get(subject_id)

#         if not subject:
#             flash('Invalid subject selected.', 'danger')
#             return redirect(url_for('add_subject'))

#         # Check if the student is already associated with the subject
#         if subject in student.subjects:
#             flash('You have already added this subject.', 'warning')
#         else:
#             student.subjects.append(subject)
#             db.session.commit()
#             flash(f'Subject "{subject.name}" added successfully!', 'success')

#         return redirect(url_for('add_subject'))

#     # Fetch subjects not yet added by the student
#     available_subjects = Subject.query.filter(~Subject.students.any(id=student_id)).all()
#     return render_template('add_subject.html', title='Add Subject', form=form, subjects=available_subjects)

# # @app.route('/add_subject', methods=['GET', 'POST'])
# # def add_subject():
# #     if 'user_id' not in session or session.get('user_role') != 'student':
# #         flash('You must be logged in as a student to access this page.', 'danger')
# #         return redirect(url_for('login'))

# #     student_id = session['user_id']

# #     if request.method == 'POST':
# #         subject_name = request.form.get('subject_name')
# #         if not subject_name:
# #             flash('Subject name cannot be empty.', 'danger')
# #             return redirect(url_for('add_subject'))

# #         # Check if the subject already exists for the student
# #         existing_subject = Subject.query.filter_by(name=subject_name, student_id=student_id).first()
# #         if existing_subject:
# #             flash('Subject already exists.', 'warning')
# #             return redirect(url_for('add_subject'))

# #         # Add the new subject
# #         new_subject = Subject(name=subject_name, student_id=student_id)
# #         db.session.add(new_subject)
# #         db.session.commit()
# #         flash('Subject added successfully!', 'success')
# #         return redirect(url_for('add_subject'))

# #     # Fetch existing subjects
# #     subjects = Subject.query.filter_by(student_id=student_id).all()
# #     return render_template('add_subject.html', title='Add Subject', subjects=subjects)

