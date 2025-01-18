from main import db

# Student model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    usn = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    attendance_records = db.relationship('Attendance', backref='student', lazy=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=True)
    subjects = db.relationship('Subject', secondary='student_subject', back_populates='students')

    def __init__(self, name, email, usn, password):
        self.name = name
        self.email = email
        self.usn = usn
        self.password = password

    def __repr__(self):
        return f"<Student(name={self.name}, email={self.email}, usn={self.usn})>"

    # Method to calculate attendance percentage
    def attendance_percentage(self, subject):
        total_classes = len(subject.attendance_records)
        attended_classes = len([att for att in subject.attendance_records if att.status])
        return (attended_classes / total_classes) * 100 if total_classes > 0 else 0

# Teacher model
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    teacher_id = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    subjects = db.relationship('Subject', back_populates='teacher', cascade='all, delete-orphan')

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
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    students = db.relationship('Student', secondary='student_subject', back_populates='subjects')
    attendance_enabled = db.Column(db.Boolean, default=False)  # Field to enable/disable attendance
    teacher = db.relationship('Teacher', back_populates='subjects')
    attendance_records = db.relationship('Attendance', backref='subject', lazy=True)

    def __init__(self, name, code, teacher):
        self.name = name
        self.code = code
        self.teacher = teacher

    def __repr__(self):
        return f"<Subject(name={self.name}, code={self.code})>"

    # Method to calculate total attendance and classes attended
    def total_classes(self):
        return len(self.attendance_records)

    def attended_classes(self):
        return len([att for att in self.attendance_records if att.status])

# Association table for many-to-many relationship between students and subjects
student_subject = db.Table(
    'student_subject',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
)

# Attendance model
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)  # To store the date when attendance is marked
    status = db.Column(db.Boolean, default=True)  # True for present, False for absent

    def __repr__(self):
        return f"<Attendance(student_id={self.student_id}, subject_id={self.subject_id}, date={self.date}, status={self.status})>"

# Course model (no changes necessary)
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    students = db.relationship('Student', backref='course', lazy=True)

    def __repr__(self):
        return f"<Course(name={self.name}, code={self.code})>"




# from main import db


# # Student model
# class Student(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False)
#     email = db.Column(db.String(100), unique=True, nullable=False)
#     usn = db.Column(db.String(20), unique=True, nullable=False)
#     password = db.Column(db.String(128), nullable=False)
#     attendance_records = db.relationship('Attendance', backref='student', lazy=True)
#     course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=True)
#     subjects = db.relationship('Subject', secondary='student_subject', back_populates='students')

#     def __init__(self, name, email, usn, password):
#         self.name = name
#         self.email = email
#         self.usn = usn
#         self.password = password

#     def __repr__(self):
#         return f"<Student(name={self.name}, email={self.email}, usn={self.usn})>"


# # Teacher model
# class Teacher(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False)
#     email = db.Column(db.String(100), unique=True, nullable=False)
#     teacher_id = db.Column(db.String(20), unique=True, nullable=False)
#     password = db.Column(db.String(128), nullable=False)
#     subjects = db.relationship('Subject', back_populates='teacher', cascade='all, delete-orphan')

#     def __init__(self, name, email, teacher_id, password):
#         self.name = name
#         self.email = email
#         self.teacher_id = teacher_id
#         self.password = password

#     def __repr__(self):
#         return f"<Teacher(name={self.name}, email={self.email}, teacher_id={self.teacher_id})>"


# # Subject model
# class Subject(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False)
#     code = db.Column(db.String(10), unique=True, nullable=False)
#     teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
#     students = db.relationship('Student', secondary='student_subject', back_populates='subjects')
#     attendance_enabled = db.Column(db.Boolean, default=False)  # Field to enable/disable attendance
#     teacher = db.relationship('Teacher', back_populates='subjects')
#     attendance_records = db.relationship('Attendance', backref='subject', lazy=True)

#     def __init__(self, name, code, teacher):
#         self.name = name
#         self.code = code
#         self.teacher = teacher

#     def __repr__(self):
#         return f"<Subject(name={self.name}, code={self.code})>"


# # Association table for many-to-many relationship between students and subjects
# student_subject = db.Table(
#     'student_subject',
#     db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
#     db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
# )


# # Attendance model
# class Attendance(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
#     subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
#     date = db.Column(db.Date, nullable=False)  # To store the date when attendance is marked
#     status = db.Column(db.Boolean, default=True)  # True for present, False for absent

#     def __repr__(self):
#         return f"<Attendance(student_id={self.student_id}, subject_id={self.subject_id}, date={self.date}, status={self.status})>"


# # Course model
# class Course(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False)
#     code = db.Column(db.String(10), unique=True, nullable=False)
#     students = db.relationship('Student', backref='course', lazy=True)

#     def __repr__(self):
#         return f"<Course(name={self.name}, code={self.code})>"



# # from main import db
# # from werkzeug.security import generate_password_hash


# # # Student model
# # class Student(db.Model):
# #     id = db.Column(db.Integer, primary_key=True)
# #     name = db.Column(db.String(50), nullable=False)
# #     email = db.Column(db.String(100), unique=True, nullable=False)
# #     usn = db.Column(db.String(20), unique=True, nullable=False)
# #     password = db.Column(db.String(128), nullable=False)
# #     attendance = db.relationship('Attendance', backref='student', lazy=True)
# #     course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=True)  # Foreign key for Course
# #     subjects = db.relationship('Subject', back_populates='student', cascade='all, delete-orphan')
    

# #     def __init__(self, name, email, usn, password):
# #         self.name = name
# #         self.email = email
# #         self.usn = usn
# #         self.password = password



# #     def __repr__(self):
# #         return f"<Student(name={self.name}, email={self.email}, usn={self.usn})>"

# # # Teacher model
# # class Teacher(db.Model):
# #     id = db.Column(db.Integer, primary_key=True)
# #     name = db.Column(db.String(50), nullable=False)
# #     email = db.Column(db.String(100), unique=True, nullable=False)
# #     teacher_id = db.Column(db.String(20), unique=True, nullable=False)
# #     password = db.Column(db.String(128), nullable=False)
# #     enable_student_attendance = db.Column(db.Boolean, default=False)
# #     subjects = db.relationship('Subject', back_populates='teacher', cascade='all, delete-orphan')
 

# #     def __init__(self, name, email, teacher_id, password):
# #         self.name = name
# #         self.email = email
# #         self.teacher_id = teacher_id
# #         self.password = password
    

# #     def __repr__(self):
# #         return f"<Teacher(name={self.name}, email={self.email}, teacher_id={self.teacher_id})>"

# # # Subject model
# # class Subject(db.Model):
# #     id = db.Column(db.Integer, primary_key=True)
# #     name = db.Column(db.String(50), nullable=False)
# #     code = db.Column(db.String(10), unique=True, nullable=False)
# #     teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
# #     students = db.relationship('Student', secondary='student_subject', back_populates='subjects')
# #     attendance_enabled = db.Column(db.Boolean, default=False)  # New field to enable attendance

# #     def __init__(self, name, code, teacher):
# #         self.name = name
# #         self.code = code
# #         self.teacher = teacher

# # # Association table for many-to-many relationship between students and subjects
# # student_subject = db.Table(
# #     'student_subject',
# #     db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
# #     db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
# # )

# # # Attendance model
# # class Attendance(db.Model):
# #     id = db.Column(db.Integer, primary_key=True)
# #     student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
# #     subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
# #     classes_attended = db.Column(db.Integer, default=0)
# #     total_classes = db.Column(db.Integer, default=0)

# #     def __repr__(self):
# #         return (f"<Attendance(student_id={self.student_id}, subject_id={self.subject_id}, "
# #                 f"classes_attended={self.classes_attended}, total_classes={self.total_classes})>")

# # # Course model (optional, if courses encompass multiple subjects)
# # class Course(db.Model):
# #     id = db.Column(db.Integer, primary_key=True)
# #     name = db.Column(db.String(50), nullable=False)
# #     code = db.Column(db.String(10), unique=True, nullable=False)
# #     students = db.relationship('Student', backref='course', lazy=True)

# #     def __repr__(self):
# #         return f"<Course(name={self.name}, code={self.code})>"
