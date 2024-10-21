from . import db
from datetime import datetime
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # e.g., 'student', 'teacher', etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

class TeacherProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    modules = db.Column(db.String(255))  # List of modules taught
    office_location = db.Column(db.String(255))
    office_hours = db.Column(db.String(255))

class StudentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dorm = db.Column(db.String(255))  # Dorm information

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(255), nullable=False)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False)
    start_period = db.Column(db.Integer, nullable=False)
    end_period = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class CourseRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)