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
    school_id = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(100))
    gender = db.Column(db.String(10))
    office_location = db.Column(db.String(100))
    office_hours = db.Column(db.String(50))
    email = db.Column(db.String(120))
    biography = db.Column(db.Text)


class StudentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    school_id = db.Column(db.String(20), unique=True, nullable=False)  # Unique student ID
    name = db.Column(db.String(100), nullable=False)  # Student name
    gender = db.Column(db.String(10), nullable=True)  # Gender
    birth = db.Column(db.String(10), nullable=True)  # Birth date in "YYYY-MM-DD" format
    email = db.Column(db.String(120), nullable=False)  # Email
    college = db.Column(db.String(100), nullable=True)  # College information
    major = db.Column(db.String(100), nullable=True)  # Major
    dorm = db.Column(db.String(255), nullable=True)  # Dorm information
    biography = db.Column(db.Text, nullable=True)  # Biography field for additional info

    # Define relationship with User
    user = db.relationship('User', backref=db.backref('student_profile', uselist=False))

class StudentGrade(db.Model):
    __tablename__ = 'student_grades'

    grade_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    grade = db.Column(db.String(5), nullable=False)

    # Define relationships to access related models
    student = db.relationship('User', backref='grades', foreign_keys=[student_id])
    course = db.relationship('Course', backref='grades', foreign_keys=[course_id])

    def __repr__(self):
        return f'<StudentGrade {self.grade}>'

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

class ForumPost(db.Model):
    __tablename__ = 'forum_post'
    post_id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_title = db.Column(db.String(255), nullable=False)
    post_content = db.Column(db.Text, nullable=False)
    post_date = db.Column(db.DateTime, default=datetime.utcnow)
    board_type = db.Column(db.String(20), nullable=False)  # "chat" or "course"
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=True)

    # Cascade delete replies when a post is deleted
    replies = db.relationship('ForumReply', cascade="all, delete-orphan", backref='post')
    # Define the relationship to access the User model
    author = db.relationship('User', backref='posts')

class ForumReply(db.Model):
    __tablename__ = 'forum_reply'
    reply_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_post.post_id'), nullable=False)
    replier_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reply_content = db.Column(db.Text, nullable=False)
    reply_date = db.Column(db.DateTime, default=datetime.utcnow)
    # Define the relationship to access the User model
    replier = db.relationship('User', backref='replies')

class LibraryStaffProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    staff_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))
    email = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(100), nullable=False)  # 图书馆部门
    position = db.Column(db.String(100), nullable=False)    # 职位
    work_hours = db.Column(db.String(100))                 # 工作时间
    biography = db.Column(db.Text, nullable=True)

    # Define relationship with User
    user = db.relationship('User', backref=db.backref('library_staff_profile', uselist=False))

class LibraryResource(db.Model):
    __tablename__ = 'library_resources'
    
    resource_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)
    availability_status = db.Column(db.String(20), nullable=False, default='available')
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<LibraryResource {self.title}>'

class EBikeLicense(db.Model):
    __tablename__ = 'e_bike_license'

    license_id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    license_plate = db.Column(db.String(20), nullable=False)
    bike_model = db.Column(db.String(50), nullable=False)
    registration_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.Enum('Pending', 'Approved', 'Expired'), default='Pending')

    owner = db.relationship('User', foreign_keys=[owner_id])
    approver = db.relationship('User', foreign_keys=[approved_by])
