from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField,SubmitField, FieldList, FormField
from wtforms.validators import DataRequired, Length, Email, EqualTo 



class SubjectForm(FlaskForm):
    class Meta:
        csrf = False  # Disable CSRF for nested forms

    subject_name = StringField('Subject Name', validators=[DataRequired(), Length(max=50)])
    subject_code = StringField('Subject Code', validators=[DataRequired(), Length(max=10)])
    submit = SubmitField('Add Subject')  # Add this line


class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    usn = StringField('USN', validators=[DataRequired(), Length(min=10, max=15)], default=None)
    submit = SubmitField('Sign Up')

class TeacherSignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    teacher_id = StringField('Teacher ID', validators=[DataRequired(), Length(max=20)])  # Optional by default
    subjects = FieldList(FormField(SubjectForm), min_entries=1, max_entries=5)
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')



 



