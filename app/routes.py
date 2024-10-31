from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, login_required, logout_user
from app.forms import RegisterForm, LoginForm, TeacherProfileForm, StudentProfileForm, CreateCourseForm, \
    RegisterCourseForm, ForumPostForm, ForumReplyForm, LibraryStaffProfileForm, AddBookForm, SearchBookForm
from app.models import User, TeacherProfile, StudentProfile, Course, CourseRegistration, db, ForumPost, ForumReply, LibraryStaffProfile, LibraryResource
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
    # 确保只有学生和老师可以访问
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
    return redirect(url_for('main.manage_books'))