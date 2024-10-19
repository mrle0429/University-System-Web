from flask import Blueprint, render_template, redirect, url_for, flash
from .forms import RegisterForm
from .models import User, db

main_routes = Blueprint('main', __name__)


@main_routes.route('/')
def index():
    return render_template('index.html')


@main_routes.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # 创建一个新的用户
        new_user = User(username=form.username.data, email=form.email.data, password=form.password.data)

        # 将新用户添加到数据库
        db.session.add(new_user)
        db.session.commit()

        # 提示用户注册成功
        flash(f'Account created for {form.username.data}!', 'success')

        # 重定向到主页
        return redirect(url_for('main.index'))

    # 渲染注册页面
    return render_template('register.html', form=form)
