from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, login_required, logout_user
from app.forms import RegisterForm, LoginForm, TeacherProfileForm, StudentProfileForm, CreateCourseForm, RegisterCourseForm
from app.models import User, TeacherProfile, StudentProfile, Course, CourseRegistration, db
from werkzeug.security import generate_password_hash, check_password_hash

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    return render_template('index.html')

@main_routes.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('This email is already registered. Please use a different email.', 'danger')
            return redirect(url_for('main.register'))

        # Create a new user
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, user_type=form.user_type.data)
        db.session.add(new_user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('main.index'))
    return render_template('register.html', form=form)

@main_routes.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.profile', user_id=user.id))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', form=form)

@main_routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@main_routes.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    if user.user_type == 'teacher':
        profile = TeacherProfile.query.filter_by(user_id=user.id).first()
        form = TeacherProfileForm(obj=profile)
        if form.validate_on_submit():
            if not profile:
                profile = TeacherProfile(user_id=user.id)
            profile.modules = form.modules.data
            profile.office_location = form.office_location.data
            profile.office_hours = form.office_hours.data
            db.session.add(profile)
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('main.profile', user_id=user.id))
        courses = Course.query.filter_by(created_by=user.id).all()
        return render_template('teacher_dashboard.html', form=form, user=user, courses=courses)
    elif user.user_type == 'student':
        profile = StudentProfile.query.filter_by(user_id=user.id).first()
        form = StudentProfileForm(obj=profile)
        if form.validate_on_submit():
            if not profile:
                profile = StudentProfile(user_id=user.id)
            profile.dorm = form.dorm.data
            db.session.add(profile)
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('main.profile', user_id=user.id))
        # Get the registered courses for this student
        registrations = CourseRegistration.query.filter_by(user_id=user.id).all()
        courses = [Course.query.get(reg.course_id) for reg in registrations]
        timetable = [['' for _ in range(5)] for _ in range(12)]
        for course in courses:
            day_index = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'].index(course.day_of_week)
            for period in range(course.start_period - 1, course.end_period):
                timetable[period][day_index] = course.course_name
        return render_template('student_dashboard.html', form=form, user=user, courses=courses, timetable=timetable)

@main_routes.route('/create_course', methods=['GET', 'POST'])
@login_required
def create_course():
    if current_user.user_type != 'teacher':
        flash('Only teachers can create courses.', 'danger')
        return redirect(url_for('main.index'))
    form = CreateCourseForm()
    if form.validate_on_submit():
        new_course = Course(
            course_name=form.course_name.data,
            course_code=form.course_code.data,
            year=form.year.data,
            semester=form.semester.data,
            day_of_week=form.day_of_week.data,
            start_period=form.start_period.data,
            end_period=form.end_period.data,
            description=form.description.data,
            created_by=current_user.id
        )
        db.session.add(new_course)
        db.session.commit()
        flash('Course created successfully!', 'success')
        return redirect(url_for('main.profile', user_id=current_user.id))
    return render_template('create_event.html', form=form)

@main_routes.route('/register_course', methods=['GET', 'POST'])
@login_required
def register_course():
    if current_user.user_type != 'student':
        flash('Only students can register for courses.', 'danger')
        return redirect(url_for('main.index'))
    form = RegisterCourseForm()
    if form.validate_on_submit():
        course = Course.query.filter_by(course_code=form.course_code.data).first()
        if not course:
            flash('Course not found. Please check the course code.', 'danger')
            return redirect(url_for('main.register_course'))
        existing_registration = CourseRegistration.query.filter_by(course_id=course.id, user_id=current_user.id).first()
        if existing_registration:
            flash('You are already registered for this course.', 'danger')
            return redirect(url_for('main.register_course'))
        new_registration = CourseRegistration(course_id=course.id, user_id=current_user.id)
        db.session.add(new_registration)
        db.session.commit()
        flash('Course registered successfully!', 'success')
        return redirect(url_for('main.profile', user_id=current_user.id))
    return render_template('register_event.html', form=form)

@main_routes.route('/edit_course/<int:course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    if current_user.user_type != 'teacher':
        flash('Only teachers can edit courses.', 'danger')
        return redirect(url_for('main.index'))
    course = Course.query.get_or_404(course_id)
    form = CreateCourseForm(obj=course)
    if form.validate_on_submit():
        course.course_name = form.course_name.data
        course.course_code = form.course_code.data
        course.year = form.year.data
        course.semester = form.semester.data
        course.day_of_week = form.day_of_week.data
        course.start_period = form.start_period.data
        course.end_period = form.end_period.data
        course.description = form.description.data
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('main.profile', user_id=current_user.id))
    return render_template('edit_course.html', form=form, course=course)

@main_routes.route('/delete_course/<int:course_id>', methods=['POST'])
@login_required
def delete_course(course_id):
    if current_user.user_type != 'teacher':
        flash('Only teachers can delete courses.', 'danger')
        return redirect(url_for('main.index'))
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('main.profile', user_id=current_user.id))

