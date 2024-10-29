from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, DateTimeField, IntegerField
from wtforms.validators import DataRequired, Length, Email

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    user_type = SelectField('User Type', choices=[('student', 'Student'), ('teacher', 'Teacher')], validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TeacherProfileForm(FlaskForm):
    modules = StringField('Modules Taught', validators=[DataRequired()])
    office_location = StringField('Office Location', validators=[DataRequired()])
    office_hours = StringField('Office Hours', validators=[DataRequired()])
    submit = SubmitField('Update Profile')

class StudentProfileForm(FlaskForm):
    dorm = StringField('Dorm', validators=[DataRequired()])
    submit = SubmitField('Update Profile')

class CreateCourseForm(FlaskForm):
    course_name = StringField('Course Name', validators=[DataRequired()])
    course_code = StringField('Course Code', validators=[DataRequired(), Length(min=2, max=20)])
    year = IntegerField('Year', validators=[DataRequired()])
    semester = SelectField('Semester', choices=[('Fall', 'Fall'), ('Spring', 'Spring')], validators=[DataRequired()])
    day_of_week = SelectField('Day of Week', choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday')], validators=[DataRequired()])
    start_period = IntegerField('Start Period', validators=[DataRequired()])
    end_period = IntegerField('End Period', validators=[DataRequired()])
    description = TextAreaField('Course Description')
    submit = SubmitField('Create Course')

class RegisterCourseForm(FlaskForm):
    course_code = StringField('Course Code', validators=[DataRequired()])
    submit = SubmitField('Register Course')

class ForumPostForm(FlaskForm):
    post_title = StringField('Title', validators=[DataRequired()])
    post_content = TextAreaField('Content', validators=[DataRequired()])
    board_type = SelectField('Board Type', choices=[('chat', 'Chat'), ('course', 'Course')], validators=[DataRequired()])
    course_id = IntegerField('Course ID')  # Only required if board_type is 'course'
    submit = SubmitField('Post')

class ForumReplyForm(FlaskForm):
    reply_content = TextAreaField('Reply', validators=[DataRequired()])
    submit = SubmitField('Reply')
