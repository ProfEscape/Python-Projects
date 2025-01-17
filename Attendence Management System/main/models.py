from main import db
from werkzeug.security import generate_password_hash


# Student model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    usn = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    attendance = db.relationship('Attendance', backref='student', lazy=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=True)  # Foreign key for Course
    subjects = db.relationship('Subject', back_populates='student', cascade='all, delete-orphan')
    

    def __init__(self, name, email, usn, password):
        self.name = name
        self.email = email
        self.usn = usn
        self.password = password



    def __repr__(self):
        return f"<Student(name={self.name}, email={self.email}, usn={self.usn})>"

# Teacher model
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    teacher_id = db.Column(db.String(20), unique=True, nullable=False)
    enable_student_attendance = db.Column(db.Boolean, default=False)
    subjects = db.relationship('Subject', backref='teacher', lazy=True)
    password = db.Column(db.String(128), nullable=False)

    def __init__(self, name, email, teacher_id, password):
        self.name = name
        self.email = email
        self.teacher_id = teacher_id
        self.password = password
    

    def __repr__(self):
        return f"<Teacher(name={self.name}, email={self.email}, teacher_id={self.teacher_id})>"

# Subject model
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

    # Relationship with the Student model
    student = db.relationship('Student', back_populates='subjects')
    
    def __repr__(self):
        return f"<Subject(name={self.name}, code={self.code})>"

# Attendance model
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    classes_attended = db.Column(db.Integer, default=0)
    total_classes = db.Column(db.Integer, default=0)

    def __repr__(self):
        return (f"<Attendance(student_id={self.student_id}, subject_id={self.subject_id}, "
                f"classes_attended={self.classes_attended}, total_classes={self.total_classes})>")

# Course model (optional, if courses encompass multiple subjects)
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    students = db.relationship('Student', backref='course', lazy=True)

    def __repr__(self):
        return f"<Course(name={self.name}, code={self.code})>"
