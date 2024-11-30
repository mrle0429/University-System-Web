from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, current_user, login_required, logout_user
from app.forms import RegisterForm, LoginForm, TeacherProfileForm, StudentProfileForm, CreateCourseForm, \
    RegisterCourseForm, ForumPostForm, ForumReplyForm, LibraryStaffProfileForm, AddBookForm, SearchBookForm, \
    AddGradeForm, EBikeForm, SecurityProfileForm, UserPreferenceForm, EditUserForm
from app.models import User, TeacherProfile, StudentProfile, Course, CourseRegistration, db, ForumPost, ForumReply, \
    LibraryStaffProfile, LibraryResource, StudentGrade, EBikeLicense, SecurityProfile, AdminProfile, UserPreference
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.logger import SystemLogger
import os

main_routes = Blueprint('main', __name__)

# 创建全局logger实例
system_logger = SystemLogger()

@main_routes.before_request
def check_banned():
    # 检查当前用户是否登录且被封禁
    if current_user.is_authenticated and current_user.is_banned:
        # 如果是被封禁用户,则登出并重定向到首页
        logout_user()
        flash('Your account has been banned. Please contact the administrator.','danger')
        return redirect(url_for('main.index'))

@main_routes.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.profile', user_id=current_user.id))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            if user.is_banned:
                system_logger.log_warning(f"Banned user attempted to login: {user.username}")
                flash('Your account has been banned.', 'danger')
                return redirect(url_for('main.index'))
            
            login_user(user)
            system_logger.log_info(f"User logged in successfully: {user.username}")
            return redirect(url_for('main.profile', user_id=user.id))
        else:
            system_logger.log_warning(f"Failed login attempt for email: {form.email.data}")
            flash('Login failed. Please check your email and password.', 'danger')
    
    return render_template('index.html', form=form)

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

    # Check if the user is a student
    if user.user_type == 'student':
        profile = StudentProfile.query.filter_by(user_id=user.id).first()
        registrations = CourseRegistration.query.filter_by(user_id=user.id).all()
        courses = [Course.query.get(reg.course_id) for reg in registrations]

        # Generate a timetable for the student
        timetable = [['' for _ in range(5)] for _ in range(12)]
        for course in courses:
            day_index = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'].index(course.day_of_week)
            for period in range(course.start_period - 1, course.end_period):
                timetable[period][day_index] = course.course_name

        return render_template(
            'student_dashboard.html',
            user=user,
            student=profile,
            courses=courses,
            timetable=timetable
        )

    # Check if the user is a teacher
    elif user.user_type == 'teacher':
        profile = TeacherProfile.query.filter_by(user_id=user.id).first()
        form = TeacherProfileForm(obj=profile)

        # Get courses created by the teacher
        courses = Course.query.filter_by(created_by=user.id).all()

        return render_template(
            'teacher_dashboard.html',
            user=user,
            profile=profile,  # Pass profile data to the template
            courses=courses
        )

    # Check if the user is a library_staff
    elif user.user_type == 'library_staff':
        profile = LibraryStaffProfile.query.filter_by(user_id=user.id).first()
        return render_template(
            'library_staff_dashboard.html',
            user=user,
            profile=profile
        )
    
    # Check if the user is a security personnel
    elif user.user_type == 'security':
        profile = SecurityProfile.query.filter_by(user_id=user.id).first()
        return render_template(
            'security_dashboard.html',
            user=user,
            profile=profile
        )
    
    elif user.user_type == 'admin':
        profile = AdminProfile.query.filter_by(user_id=user.id).first()
        return render_template(
            'admin_dashboard.html',
            user=user,
            profile=profile
        )

    # If user_type is not recognized, return an error
    flash("Invalid user type.", "danger")
    return redirect(url_for('main.profile', user_id=user_id))

@main_routes.route('/edit_profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):
    user = User.query.get_or_404(user_id)

    # Ensure only the current user can edit their profile
    if user.id != current_user.id:
        flash("You are not authorized to edit this profile.", "danger")
        return redirect(url_for('main.profile', user_id=user_id))

    # Handle student profile editing
    if user.user_type == 'student':
        profile = StudentProfile.query.filter_by(user_id=user.id).first()
        form = StudentProfileForm(obj=profile)

        if form.validate_on_submit():
            if not profile:
                profile = StudentProfile(user_id=user.id)
            profile.school_id = form.school_id.data
            profile.name = form.name.data
            profile.gender = form.gender.data
            profile.birth = form.birth.data
            profile.email = form.email.data
            profile.college = form.college.data
            profile.major = form.major.data
            profile.dorm = form.dorm.data
            profile.biography = form.biography.data

            db.session.add(profile)
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('main.profile', user_id=user.id))

        return render_template('edit_profile.html', form=form, user=user)

    # Handle teacher profile editing
    elif user.user_type == 'teacher':
        profile = TeacherProfile.query.filter_by(user_id=user.id).first()
        form = TeacherProfileForm(obj=profile)

        if form.validate_on_submit():
            if not profile:
                profile = TeacherProfile(user_id=user.id)
            profile.school_id = form.school_id.data
            profile.name = form.name.data
            profile.gender = form.gender.data
            profile.office_location = form.office_location.data
            profile.office_hours = form.office_hours.data
            profile.email = form.email.data
            profile.biography = form.biography.data

            db.session.add(profile)
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('main.profile', user_id=user.id))

        return render_template('edit_profile.html', form=form, user=user)

    # Check if the user is a library_staff
    elif user.user_type == 'library_staff':
        profile = LibraryStaffProfile.query.filter_by(user_id=user.id).first()
        form = LibraryStaffProfileForm(obj=profile)
        
        if form.validate_on_submit():
            if not profile:
                profile = LibraryStaffProfile(user_id=user.id)
            profile.staff_id = form.staff_id.data
            profile.name = form.name.data
            profile.gender = form.gender.data
            profile.email = form.email.data
            profile.department = form.department.data
            profile.position = form.position.data
            profile.work_hours = form.work_hours.data
            profile.biography = form.biography.data
            
            db.session.add(profile)
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('main.profile', user_id=user.id))
            
        return render_template('edit_profile.html', form=form, user=user)
    
    # Handle security personnel profile editing
    elif user.user_type == 'security':
        profile = SecurityProfile.query.filter_by(user_id=user.id).first()
        form = SecurityProfileForm(obj=profile)

        if form.validate_on_submit():
            if not profile:
                profile = SecurityProfile(user_id=user.id)
            profile.staff_id = form.staff_id.data
            profile.name = form.name.data
            profile.gender = form.gender.data
            profile.shift_hours = form.shift_hours.data
            profile.assigned_area = form.assigned_area.data
            profile.email = form.email.data
            profile.biography = form.biography.data

            db.session.add(profile)
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('main.profile', user_id=user.id))
        
        return render_template('edit_profile.html', form=form, user=user)

    flash("Invalid user type.", "danger")
    return redirect(url_for('main.profile', user_id=user_id))

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

@main_routes.route('/forum/<string:board_type>')
@login_required
def forum(board_type):

    # 确只有学生和老师可以访问
    if current_user.user_type not in ['student', 'teacher']:
        flash("You are not authorized to access this board.", "danger")
        return redirect(url_for('main.index'))

    # 检查 board_type 是否有效
    if board_type not in ['chat', 'course']:
        flash("Invalid board type.", "danger")
        return redirect(url_for('main.index'))

    if board_type == "course":
        if current_user.user_type == "student":
            # Get courses the student is registered for
            registrations = CourseRegistration.query.filter_by(user_id=current_user.id).all()
            course_ids = [reg.course_id for reg in registrations]
            posts = ForumPost.query.filter(ForumPost.board_type == "course", ForumPost.course_id.in_(course_ids)).all()
        else:
            posts = ForumPost.query.filter_by(board_type="course").all()
    else:
        posts = ForumPost.query.filter_by(board_type="chat").all()

    return render_template('forum.html', posts=posts, board_type=board_type)

@main_routes.route('/forum/<string:board_type>/create', methods=['GET', 'POST'])
@login_required
def create_post(board_type):
    form = ForumPostForm(board_type=board_type)  # Set the board type in the form

    if form.validate_on_submit():
        new_post = ForumPost(
            author_id=current_user.id,
            post_title=form.post_title.data,
            post_content=form.post_content.data,
            board_type=board_type,  # Directly from URL param
            course_id=form.course_id.data if board_type == "course" else None
        )
        db.session.add(new_post)
        db.session.commit()
        system_logger.log_info(f"User {current_user.username} created a new post in {board_type} board")
        flash("Post created successfully!", "success")
        return redirect(url_for('main.forum', board_type=board_type))
    return render_template('create_post.html', form=form, board_type=board_type)

@main_routes.route('/forum/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def view_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    form = ForumReplyForm()
    if form.validate_on_submit():
        new_reply = ForumReply(
            post_id=post_id,
            replier_id=current_user.id,
            reply_content=form.reply_content.data
        )
        db.session.add(new_reply)
        db.session.commit()
        flash("Reply posted successfully!", "success")
        return redirect(url_for('main.view_post', post_id=post_id))

    replies = ForumReply.query.filter_by(post_id=post_id).all()
    return render_template('view_post.html', post=post, replies=replies, form=form)

@main_routes.route('/forum/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    if post.author_id != current_user.id:
        flash("You can only delete your own posts.", "danger")
        return redirect(url_for('main.forum', board_type=post.board_type))

    db.session.delete(post)
    db.session.commit()
    flash("Post and its replies have been deleted.", "success")
    return redirect(url_for('main.forum', board_type=post.board_type))

@main_routes.route('/forum/reply/<int:reply_id>/delete', methods=['POST'])
@login_required
def delete_reply(reply_id):
    reply = ForumReply.query.get_or_404(reply_id)
    if reply.replier_id != current_user.id:
        flash("You can only delete your own replies.", "danger")
        return redirect(url_for('main.view_post', post_id=reply.post_id))

    db.session.delete(reply)
    db.session.commit()
    flash("Reply has been deleted.", "success")
    return redirect(url_for('main.view_post', post_id=reply.post_id))

@main_routes.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    # 检查是否是图书馆工作人员
    if current_user.user_type != 'library_staff':
        flash('Access denied. Library staff only.', 'danger')
        return redirect(url_for('main.index'))
    
    form = AddBookForm()
    if form.validate_on_submit():
        new_book = LibraryResource(
            title=form.title.data,
            author=form.author.data,
            publication_year=form.publication_year.data,
            category=form.category.data,
            availability_status='available'
        )
        db.session.add(new_book)
        db.session.commit()
        flash('New book added successfully!', 'success')
        return redirect(url_for('main.profile', user_id=current_user.id))
    
    return render_template('add_book.html', form=form)

@main_routes.route('/search_books', methods=['GET', 'POST'])
def search_books():
    form = SearchBookForm()
    query = LibraryResource.query
    
    if form.validate_on_submit():
        if form.title.data:
            query = query.filter(LibraryResource.title.ilike(f'%{form.title.data}%'))
        if form.author.data:
            query = query.filter(LibraryResource.author.ilike(f'%{form.author.data}%'))
        if form.publication_year.data:
            query = query.filter(LibraryResource.publication_year == form.publication_year.data)
        if form.availability_status.data:
            query = query.filter(LibraryResource.availability_status == form.availability_status.data)
    
    books = query.all()
    return render_template('search_books.html', form=form, books=books)

@main_routes.route('/library_statistics')
@login_required
def library_statistics():
    if current_user.user_type != 'library_staff':
        flash('Access denied. Library staff only.', 'danger')
        return redirect(url_for('main.index'))
    
    # 获取基本统计数据
    total_books = LibraryResource.query.count()
    available_books = LibraryResource.query.filter_by(availability_status='available').count()
    borrowed_books = LibraryResource.query.filter_by(availability_status='borrowed').count()
    reserved_books = LibraryResource.query.filter_by(availability_status='reserved').count()
    
    # 获取分类统计
    category_stats = db.session.query(
        LibraryResource.category, 
        db.func.count(LibraryResource.resource_id)
    ).group_by(LibraryResource.category).all()
    
    return render_template('library_statistics.html',
                         total_books=total_books,
                         available_books=available_books,
                         borrowed_books=borrowed_books,
                         reserved_books=reserved_books,
                         category_stats=category_stats)

@main_routes.route('/manage_books', methods=['GET', 'POST'])
@login_required
def manage_books():
    if current_user.user_type != 'library_staff':
        flash('Access denied. Library staff only.', 'danger')
        return redirect(url_for('main.index'))
    
    search_form = SearchBookForm()
    add_book_form = AddBookForm()
    query = LibraryResource.query
    
    if search_form.validate_on_submit():
        if search_form.title.data:
            query = query.filter(LibraryResource.title.ilike(f'%{search_form.title.data}%'))
        if search_form.author.data:
            query = query.filter(LibraryResource.author.ilike(f'%{search_form.author.data}%'))
        if search_form.publication_year.data:
            query = query.filter(LibraryResource.publication_year == search_form.publication_year.data)
        if search_form.availability_status.data:
            query = query.filter(LibraryResource.availability_status == search_form.availability_status.data)
    
    books = query.all()
    return render_template('manage_books.html', 
                         search_form=search_form, 
                         add_book_form=add_book_form, 
                         books=books)

@main_routes.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    if current_user.user_type != 'library_staff':
        flash('Access denied. Library staff only.', 'danger')
        return redirect(url_for('main.index'))
    
    book = LibraryResource.query.get_or_404(book_id)
    form = AddBookForm(obj=book)
    
    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.publication_year = form.publication_year.data
        book.category = form.category.data
        book.availability_status = form.availability_status.data  # 更新借阅状态
        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('main.manage_books'))
    
    return render_template('edit_book.html', form=form, book=book)

@main_routes.route('/delete_book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    if current_user.user_type != 'library_staff':
        flash('Access denied. Library staff only.', 'danger')
        return redirect(url_for('main.index'))
    
    book = LibraryResource.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!', 'success')
    system_logger.log_info(f"Library staff {current_user.username} deleted book: {book_title}")
    return redirect(url_for('main.manage_books'))

@main_routes.route('/view_grades/<int:student_id>', methods=['GET'])
@login_required
def view_grades(student_id):
    if current_user.user_type != 'student' or current_user.id != student_id:
        flash("You are not authorized to view this page.", "danger")
        return redirect(url_for('main.index'))

    # 查询该学生的所有成绩
    grades = StudentGrade.query.filter_by(student_id=student_id).all()

    # 将课程名称与成绩关联
    grade_data = [
        {
            'course_name': Course.query.get(grade.course_id).course_name,
            'grade': grade.grade
        }
        for grade in grades
    ]

    return render_template('view_grades.html', grade_data=grade_data)


@main_routes.route('/add_grade', methods=['GET', 'POST'])
@login_required
def add_grade():
    course_id = request.args.get('course_id', type=int)
    student_id = request.args.get('student_id', type=int)

    # 检查用户权限，仅允许教师访问
    if current_user.user_type != 'teacher':
        flash("You are not authorized to access this page.", "danger")
        return redirect(url_for('main.index'))

    # 查询表单
    form = AddGradeForm()
    if form.validate_on_submit():
        # 检查是否已存在该学生和课程的成绩记录
        grade_entry = StudentGrade.query.filter_by(student_id=student_id, course_id=course_id).first()

        if grade_entry:
            # 更新现有成绩
            grade_entry.grade = form.grade.data
            system_logger.log_info(f"Teacher {current_user.username} updated grade for student {student_id} in course {course_id}")
            flash("Grade updated successfully!", "success")
        else:
            # 创建新的成绩记录
            grade_entry = StudentGrade(student_id=student_id, course_id=course_id, grade=form.grade.data)
            db.session.add(grade_entry)
            system_logger.log_info(f"Teacher {current_user.username} added new grade for student {student_id} in course {course_id}")
            flash("Grade added successfully!", "success")

        db.session.commit()
        return redirect(url_for('main.select_grade_entry'))

    return render_template('add_grade.html', form=form)


@main_routes.route('/select_grade_entry', methods=['GET', 'POST'])
@login_required
def select_grade_entry():
    # 检查用户权限，仅允许教师访问
    if current_user.user_type != 'teacher':
        flash("You are not authorized to access this page.", "danger")
        return redirect(url_for('main.index'))

    # 获取当前教师创建的课程
    courses = Course.query.filter_by(created_by=current_user.id).all()

    # 初始化学生为空，在前端根据选择的课程动态加载
    students = []

    return render_template('select_grade_entry.html', courses=courses, students=students)

@main_routes.route('/get_students_by_course/<int:course_id>', methods=['GET'])
@login_required
def get_students_by_course(course_id):
    # 验证该课程是否由当前教师创建
    course = Course.query.filter_by(id=course_id, created_by=current_user.id).first()
    if not course:
        return jsonify({'error': 'Unauthorized access'}), 403

    # 查询注册了该课程的学生
    registrations = CourseRegistration.query.filter_by(course_id=course_id).all()
    students = [
        {'id': reg.user_id, 'username': User.query.get(reg.user_id).username}
        for reg in registrations
    ]

    return jsonify({'students': students})

@main_routes.route('/e_bike_management', methods=['GET', 'POST'])
@login_required
def e_bike_management():
    if current_user.user_type != 'student':
        flash("You are not authorized to access this page.", "danger")
        return redirect(url_for('main.index'))

    # 查询当前学生的电动车信息
    e_bike = EBikeLicense.query.filter_by(owner_id=current_user.id).first()
    form = EBikeForm(obj=e_bike)

    if form.validate_on_submit():
        if not e_bike:
            e_bike = EBikeLicense(owner_id=current_user.id)
        e_bike.license_plate = form.license_plate.data
        e_bike.bike_model = form.bike_model.data
        e_bike.status = 'Pending'  # 每次创建或修改后自动变为“申请”状态
        e_bike.registration_date = None
        e_bike.expiration_date = None
        e_bike.approved_by = None
        db.session.add(e_bike)
        db.session.commit()
        flash("E-bike registration updated successfully!", "success")
        return redirect(url_for('main.e_bike_management'))

    return render_template('e_bike_management.html', form=form, e_bike=e_bike)



@main_routes.route('/manage_ebikes', methods=['GET'])
@login_required
def manage_ebikes():
    if current_user.user_type != 'security':
        flash('Access denied. Security personnel only.', 'danger')
        return redirect(url_for('main.index'))

    # 获取所有电动车申请，并按 ID 倒序排列
    ebikes = EBikeLicense.query.order_by(EBikeLicense.license_id.desc()).all()
    return render_template('manage_ebikes.html', ebikes=ebikes)


@main_routes.route('/approve_ebike/<int:ebike_id>', methods=['POST'])
@login_required
def approve_ebike(ebike_id):
    if current_user.user_type != 'security':
        flash('Access denied. Security personnel only.', 'danger')
        return redirect(url_for('main.index'))

    ebike = EBikeLicense.query.get_or_404(ebike_id)
    ebike.status = 'Approved'
    ebike.registration_date = request.form['registration_date']
    ebike.expiration_date = request.form['expiration_date']
    ebike.approved_by = current_user.id
    db.session.commit()
    flash('E-bike approved successfully!', 'success')
    return redirect(url_for('main.manage_ebikes'))

@main_routes.route('/reject_ebike/<int:ebike_id>', methods=['POST'])
@login_required
def reject_ebike(ebike_id):
    if current_user.user_type != 'security':
        flash('Access denied. Security personnel only.', 'danger')
        return redirect(url_for('main.index'))

    ebike = EBikeLicense.query.get_or_404(ebike_id)
    ebike.status = 'Rejected'
    db.session.commit()
    flash('E-bike rejected successfully!', 'success')
    return redirect(url_for('main.manage_ebikes'))

@main_routes.route('/cancel_ebike/<int:ebike_id>', methods=['POST'])
@login_required
def cancel_ebike(ebike_id):
    if current_user.user_type != 'security':
        flash('Access denied. Security personnel only.', 'danger')
        return redirect(url_for('main.index'))

    ebike = EBikeLicense.query.get_or_404(ebike_id)
    ebike.status = 'Cancelled'
    ebike.registration_date = None
    ebike.expiration_date = None
    ebike.approved_by = None
    db.session.commit()
    flash('E-bike registration cancelled successfully!', 'success')
    return redirect(url_for('main.manage_ebikes'))

@main_routes.route('/visitor')
def visitor():
    return render_template('visitor.html')

@main_routes.route('/contact')
def contact():
    return render_template('contact.html')

@main_routes.route('/admin/manage_users', methods=['GET', 'POST'])
@login_required
def manage_users():
    if current_user.user_type != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('main.index'))

    users = User.query.all()
    system_logger.log_info(f"Admin {current_user.username} accessed user management")
    return render_template('manage_users.html', users=users)

#管理员创建用户
@main_routes.route('/admin/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if current_user.user_type != 'admin':
        flash('访问被拒绝。仅限管理员使用。', 'danger')
        return redirect(url_for('main.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('该邮箱已被注册。请使用其他邮箱。', 'danger')
            return redirect(url_for('main.create_user'))
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            user_type=form.user_type.data
        )
        db.session.add(new_user)
        db.session.commit()
        system_logger.log_info(f"Admin {current_user.username} created new user: {new_user.username} ({new_user.user_type})")
        flash(f'用户 {form.username.data} 创建成功！', 'success')
        return redirect(url_for('main.manage_users'))
    return render_template('create_user.html', form=form)

@main_routes.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.user_type != 'admin':
        flash('访问被拒绝。仅限管理员使用。', 'danger')
        return redirect(url_for('main.index'))

    try:
        user = User.query.get_or_404(user_id)
        username = user.username
        user_type = user.user_type
        # 1. 根据用户类型处理特定关联数据
        if user.user_type == 'student':
            # 处理学生相关数据
            CourseRegistration.query.filter_by(user_id=user.id).delete()
            StudentGrade.query.filter_by(student_id=user.id).delete()
            EBikeLicense.query.filter_by(owner_id=user.id).delete()
            StudentProfile.query.filter_by(user_id=user.id).delete()

        elif user.user_type == 'teacher':
            # 处理教师相关数据
            courses = Course.query.filter_by(created_by=user.id).all()
            for course in courses:
                StudentGrade.query.filter_by(course_id=course.id).delete()
                CourseRegistration.query.filter_by(course_id=course.id).delete()
            Course.query.filter_by(created_by=user.id).delete()
            TeacherProfile.query.filter_by(user_id=user.id).delete()

        elif user.user_type == 'security':
            # 处理安保人员相关数据
            EBikeLicense.query.filter_by(approved_by=user.id).update({EBikeLicense.approved_by: None})
            SecurityProfile.query.filter_by(user_id=user.id).delete()

        elif user.user_type == 'library_staff':
            # 处理图书管理员相关数据
            LibraryStaffProfile.query.filter_by(user_id=user.id).delete()
        
        elif user.user_type == 'admin':
            # 检查是否是最后一个管理员
            admin_count = User.query.filter_by(user_type='admin').count()
            if admin_count <= 1:
                from flask import session
                session['_flashes'] = [(u'danger', u'Cannot delete the last admin account.')]
                return redirect(url_for('main.manage_users'))
            AdminProfile.query.filter_by(user_id=user.id).delete()

        # 2. 处理论坛相关数据（除了安保人员）
        if user.user_type != 'security':
            posts = ForumPost.query.filter_by(author_id=user.id).all()
            for post in posts:
                ForumReply.query.filter_by(post_id=post.post_id).delete()
            ForumReply.query.filter_by(replier_id=user.id).delete()
            ForumPost.query.filter_by(author_id=user.id).delete()
        
        # 3. 删除用户偏好设置（所有类型用户都有）
        UserPreference.query.filter_by(user_id=user.id).delete()
        
        # 4. 最后删除用户本身
        db.session.delete(user)
        db.session.commit()
        
        system_logger.log_info(f"Admin {current_user.username} deleted user: {username} ({user_type})")
        flash('User Delete Success!', 'success')
        return redirect(url_for('main.manage_users'))
        
    except Exception as e:
        system_logger.log_error(f"Error deleting user {user_id}: {str(e)}")
        db.session.rollback()
        flash(f'Delete Error:{str(e)}', 'danger')
        return redirect(url_for('main.manage_users'))
    

@main_routes.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    # 获取或创建用户偏好
    user_pref = UserPreference.query.filter_by(user_id=current_user.id).first()
    if not user_pref:
        user_pref = UserPreference(user_id=current_user.id)
        db.session.add(user_pref)
        db.session.commit()
    
    form = UserPreferenceForm(obj=user_pref)
    
    if form.validate_on_submit():
        user_pref.theme = form.theme.data
        user_pref.font_size = form.font_size.data
        db.session.commit()
        flash('Preferences updated successfully!', 'success')
        return redirect(url_for('main.preferences'))
        
    return render_template('preferences.html', form=form)

@main_routes.route('/admin/manage_courses')
@login_required
def manage_courses():
    if current_user.user_type != 'admin':
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('main.index'))
    
# Get all courses
    courses = Course.query.all()
    

    
    return render_template('manage_courses.html', courses=courses)

@main_routes.route('/admin/delete_course/<int:course_id>', methods=['POST'])
@login_required
def delete_course_admin(course_id):
    if current_user.user_type != 'admin':
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('main.index'))

    try:
        course = Course.query.get_or_404(course_id)
        
        # Delete all course-related data
        # 1. Delete grades
        StudentGrade.query.filter_by(course_id=course.id).delete()
        
        # 2. Delete course registrations
        CourseRegistration.query.filter_by(course_id=course.id).delete()
        
        # 3. Delete forum posts and replies
        course_posts = ForumPost.query.filter_by(course_id=course.id).all()
        for post in course_posts:
            ForumReply.query.filter_by(post_id=post.post_id).delete()
        ForumPost.query.filter_by(course_id=course.id).delete()
        
        # 4. Delete the course itself
        db.session.delete(course)
        db.session.commit()
        
        flash('Course deleted successfully!', 'success')
        return redirect(url_for('main.manage_courses'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting course: {str(e)}', 'danger')
        return redirect(url_for('main.manage_courses'))

@main_routes.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.user_type != 'admin':
        flash('访问被拒绝。仅限管理员使用。', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    
    if form.validate_on_submit():

        user.user_type = form.user_type.data
        
        if form.password.data:  # 只有当输入了新密码时才更新密码
            user.password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            
        db.session.commit()
        flash(f'User {user.username} update success !', 'success')
        return redirect(url_for('main.manage_users'))
        
    return render_template('edit_user.html', form=form, user=user)

@main_routes.route('/admin/ban_user/<int:user_id>', methods=['POST'])
@login_required
def ban_user(user_id):
    if current_user.user_type != 'admin':
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    user.is_banned = True
    db.session.commit()
    system_logger.log_warning(f"Admin {current_user.username} banned user: {user.username}")
    flash(f'User {user.username} has been banned.', 'success')
    return redirect(url_for('main.manage_users'))

@main_routes.route('/admin/unban_user/<int:user_id>', methods=['POST'])
@login_required
def unban_user(user_id):
    if current_user.user_type != 'admin':
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    user.is_banned = False
    db.session.commit()
    system_logger.log_info(f"Admin {current_user.username} unbanned user: {user.username}")
    flash(f'User {user.username} has been unbanned.', 'success')
    return redirect(url_for('main.manage_users'))

@main_routes.route('/admin/view_logs')
@login_required
def view_logs():
    if current_user.user_type != 'admin':
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('main.index'))
    
    # 获取日志文件列表
    log_dir = 'logs'
    log_files = []
    if os.path.exists(log_dir):
        log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
        log_files.sort(reverse=True)  # 最新的文件在前
    
    # 读取选定的日志文件
    selected_log = request.args.get('file', '')
    log_content = {'errors': [], 'warnings': [], 'info': []}
    
    if selected_log and selected_log in log_files:
        with open(os.path.join(log_dir, selected_log), 'r', encoding='utf-8') as f:
            for line in f:
                if 'ERROR' in line:
                    log_content['errors'].append(line)
                elif 'WARNING' in line:
                    log_content['warnings'].append(line)
                elif 'INFO' in line:
                    log_content['info'].append(line)
    
    return render_template('view_logs.html',
                         log_files=log_files,
                         selected_log=selected_log,
                         log_content=log_content)


@main_routes.errorhandler(Exception)
def handle_error(error):
    system_logger.log_error(f"System error: {str(error)}")
    return 'Internal Server Error', 500