from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, DateTimeField, IntegerField
from wtforms.validators import DataRequired, Length, Email, Optional

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    user_type = SelectField('User Type', choices=[('student', 'Student'), ('teacher', 'Teacher'), ('library_staff', 'Library Staff'),('security', 'Security Personnel')], validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TeacherProfileForm(FlaskForm):
    school_id = StringField('School ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    office_location = StringField('Office Location', validators=[DataRequired()])
    office_hours = StringField('Office Hours', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    biography = TextAreaField('Biography')
    submit = SubmitField('Update Profile')


class StudentProfileForm(FlaskForm):
    school_id = StringField('School ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    birth = StringField('Birth Date (YYYY-MM-DD)', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    college = StringField('College', validators=[DataRequired()])
    major = StringField('Major', validators=[DataRequired()])
    dorm = StringField('Dorm', validators=[DataRequired()])
    biography = TextAreaField('Biography')
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

class LibraryStaffProfileForm(FlaskForm):
    staff_id = StringField('Staff ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    department = StringField('Department', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    work_hours = StringField('Work Hours')
    biography = TextAreaField('Biography')
    submit = SubmitField('Update Profile')

class SecurityProfileForm(FlaskForm):
    staff_id = StringField('Staff ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    shift_hours = StringField('Shift Hours', validators=[DataRequired()])
    assigned_area = StringField('Assigned Area', validators=[DataRequired()])
    biography = TextAreaField('Biography')
    submit = SubmitField('Update Profile')

class AddBookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    publication_year = IntegerField('Publication Year', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('fiction', 'Fiction'),
        ('non-fiction', 'Non-Fiction'),
        ('textbook', 'Textbook'),
        ('reference', 'Reference'),
        ('magazine', 'Magazine'),
        ('comic', 'Comic'),
        ('graphic_novel', 'Graphic Novel'),
        ('science', 'Science'),
        ('history', 'History'),
        ('biography', 'Biography'),
        ('children', 'Children'),
        ('mystery', 'Mystery'),
        ('fantasy', 'Fantasy'),
        ('romance', 'Romance'),
        ('horror', 'Horror'),
        ('self_help', 'Self Help'),
        ('travel', 'Travel'),
        ('health', 'Health'),
        ('cookbook', 'Cookbook'),
        ('poetry', 'Poetry'),
        ('drama', 'Drama'),
        ('adventure', 'Adventure'),
        ('science_fiction', 'Science Fiction'),
        ('technology', 'Technology'),
        ('philosophy', 'Philosophy'),
        ('religion', 'Religion'),
        ('politics', 'Politics'),
        ('art', 'Art'),
        ('music', 'Music'),
        ('sports', 'Sports'),
        ('education', 'Education'),
        ('psychology', 'Psychology'),
        ('law', 'Law'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    availability_status = SelectField('Availability Status', choices=[
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('lost', 'Lost')
    ], validators=[DataRequired()])
    submit = SubmitField('Add Book')

class SearchBookForm(FlaskForm):
    title = StringField('Title')
    author = StringField('Author')
    publication_year = IntegerField('Publication Year', validators=[Optional()])
    availability_status = SelectField('Status', choices=[
        ('', 'All'),
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('lost', 'Lost')
    ])
    submit = SubmitField('Search')

class AddGradeForm(FlaskForm):
    grade = SelectField('Grade', choices=[
        ('A+', 'A+'), ('A', 'A'), ('A-', 'A-'),
        ('B+', 'B+'), ('B', 'B'), ('B-', 'B-'),
        ('C+', 'C+'), ('C', 'C'), ('C-', 'C-'),
        ('D+', 'D+'), ('D', 'D'), ('F', 'F')
    ], validators=[DataRequired()])
    submit = SubmitField('Add Grade')

class EBikeForm(FlaskForm):
    license_plate = StringField('License Plate', validators=[DataRequired(), Length(max=20)])
    bike_model = StringField('Bike Model', validators=[DataRequired(), Length(max=50)])

class UserPreferenceForm(FlaskForm):
    theme = SelectField('Theme', choices=[
        ('light', 'Light Mode'),
        ('dark', 'Dark Mode'),
        ('blue', 'Blue Mode')
    ], validators=[DataRequired()])
    font_size = SelectField('Font Size', choices=[
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large')
    ], validators=[DataRequired()])
    submit = SubmitField('Save Preferences')

class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', render_kw={'readonly': True})     
    password = PasswordField('Password (leave blank to keep unchanged)')
    user_type = SelectField('User Type', 
                          choices=[('student', 'Student'),
                                 ('teacher', 'Teacher'),
                                 ('library_staff', 'Library Staff'),
                                 ('security', 'Security'),],
                          validators=[DataRequired()])
    submit = SubmitField('Update User')

