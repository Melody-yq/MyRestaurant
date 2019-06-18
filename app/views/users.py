import os
from flask import Blueprint, render_template, url_for, request, flash, get_flashed_messages, redirect, current_app
from app.forms import RegisterForm, LoginForm, UploadForm, PasswordForm, FindPassword, InputPassword, ChangeEmailForm
from app.models import User
from app.exts import db, photos
from app.email import send_mail
from flask_login import login_required, login_user, logout_user, current_user
from PIL import Image
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

users = Blueprint('users', __name__)


@users.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        u = User(username=form.username.data, password=form.password.data, email=form.email.data)
        db.session.add(u)
        db.session.commit()

        # 生成token  用u对象调用模型中的方法
        token = u.generate_active_token()
        send_mail(u.email, '账户激活', 'email/activate', username=u.username, token=token)
        flash("恭喜注册成功,请点击邮件中的链接完成激活")
        return redirect(url_for('users.login'))
    return render_template('user/register.html', form=form)


# 这个方法用来验证token  给用户邮箱发送过去一个完整的url
@users.route('/active/<token>', methods=['GET', 'POST'])
def active(token):
    if User.check_active_token(token):
        flash("账户激活成功")
        return redirect(url_for('users.login'))
    else:
        flash("账户激活失败")
        return redirect(url_for('main.index'))


# 登陆
@users.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username=form.username.data).first()
        if not u:
            flash("该用户名不存在")
        elif not u.confirmed:
            flash("该账户没有激活,请激活后登录")
        elif u.verify_password(form.password.data):
            login_user(u, remember=form.remember.data)
            flash("登录成功")
            return redirect(request.args.get('next') or url_for("main.index"))
        else:
            flash("密码不正确")
    return render_template('user/login2.html', form=form)


@users.route('/logout/', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash("退出登录成功")
    return redirect(url_for('main.index'))


@users.route('/test/', methods=['GET', 'POST'])
@login_required
def test():
    return 'this is test'


# 修改头像
@users.route('/change_icon/', methods=['GET', 'POST'])
@login_required
def change_icon():
    img_url = ''
    form = UploadForm()
    if form.validate_on_submit():
        # 获取文件后缀
        suffix = os.path.splitext(form.icon.data.filename)[1]
        # 随机文件名  拼接
        filename = random_string() + suffix
        photos.save(form.icon.data, name=filename)
        pathname = os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], filename)
        flash(pathname)
        img = Image.open(pathname)
        img.thumbnail((128, 128))
        img.save(pathname)
        # 这里，判断用户的头像是否为默认头像
        if current_user.icon != 'default.jpg':
            remove_name = os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], current_user.icon)
            os.remove(remove_name)
        current_user.icon = filename  # 将新上传的文件名 赋值给 用户的头像
        db.session.add(current_user)  # 保存在数据库中
        flash("头像上传成功")
        return redirect(url_for("users.change_icon"))
    img_url = photos.url(current_user.icon)
    return render_template('user/change_icon.html', form=form, img_url=img_url)


def random_string(length=20):
    import random
    base_str = 'abc123defhijklmnopqrstuvwxyz4567890'
    return ''.join(random.choice(base_str) for i in range(length))


# 修改邮箱
@users.route('/change_email/', methods=['GET', 'POST'])
@login_required
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        user = User.query.filter(User.username == current_user.username).first()
        if user.verify_password(form.password.data):
            current_user.email = form.email.data
            db.session.add(current_user)
            flash("修改成功")
            return redirect(url_for("users.information"))
        else:
            flash('用户名或密码输入错误')
    return render_template('user/change_email.html', form=form)


# 修改密码
@users.route('/change_password/', methods=['GET', 'POST'])
@login_required
def change_password():
    form = PasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.pre_password.data):
            # 首先要验证旧密码的正确性,如果错误要有处理
            current_user.password = form.new_password.data
            db.session.add(current_user)
            flash('修改密码成功')
            return redirect(url_for('main.index'))
        else:
            flash('修改密码失败，请重新尝试')
    return render_template('user/change_password.html', form=form)


# 找回密码
@users.route('/find_password/', methods=['GET', 'POST'])
def find_password():
    form = FindPassword()
    if form.validate_on_submit():
        # 获得当前的用户  根据填入的username
        u = User.query.filter_by(username=form.username.data).first()
        if not u:
            flash("该用户名不存在，请重新输入")
        # elif current_user.username != u.username:
        #     flash("请输入您自己的正确的用户名")
        else:
            # 发送邮件，找回密码（修改密码）
            # 生成token  用u对象调用模型中的方法
            token = u.generate_active_token()
            send_mail(u.email, '找回密码', 'email/find', username=u.username, token=token)
            flash("链接已发送到邮箱，请点击邮箱中的链接找回密码")
    return render_template('user/find_password.html', form=form)


# 这个方法用来验证token  给用户邮箱发送过去一个完整的url
@users.route('/check_token/<token>', methods=['GET', 'POST'])
def check_token(token):
    if User.check_active_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            # return False
            flash('点击链接时操作失败')
        # 这个id是从 token中解析出来的  然后根据id 到数据库中查找  对应的数据进行更新
        u = User.query.get(data.get('id'))
        if not u:
            flash("该用户不存在，请重新尝试")
            return redirect(url_for('users.index'))
        else:
            ## 用户点击了链接，跳转到修改密码的界面进行修改
            # return redirect(url_for('users.input_password'))
            form = InputPassword()
            if form.validate_on_submit():
                # 表单数据验证成功
                u.password = form.new_password.data
                db.session.add(u)
                flash('修改密码成功，请登陆')
                return redirect(url_for('users.login'))
            else:
                flash('input修改密码失败，请重新尝试')
            return render_template('user/inputPassword.html', form=form)
    else:
        flash("check_token,密码修改失败")
        return redirect(url_for('main.index'))


# 填写新的密码的操作
@users.route('/input_password/', methods=['GET', 'POST'])
def input_password():
    form = InputPassword()
    if form.validate_on_submit():
        current_user.password = form.new_password.data
        db.session.add(current_user)
        flash('修改密码成功')
        return redirect(url_for('main.index'))
    else:
        flash('input修改密码失败,请重新尝试')
    return render_template('user/inputPassword.html', form=form)


# 查看个人资料
@users.route('/information')
def information():
    return render_template('user/userInfo.html')
