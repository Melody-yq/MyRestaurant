from flask import Blueprint, render_template, request, flash, get_flashed_messages, redirect, current_app, url_for
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app.models import Posts
from app.forms import PostForm
from flask_login import current_user
from app.exts import db
from app.models import User, Posts
from flask_login import login_required, login_user, logout_user, current_user
import os

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def index():
    u = None
    # 判断当前是否登陆
    if current_user.is_authenticated:  # 如果登录
        # 获取当前用户
        u = current_user._get_current_object()
    users1 = User.query.all()
    users = users1[1:5]
    # 获取所有的帖子（按时间顺序）

    posts1 = Posts.query.order_by(Posts.timestamp.desc()).all()
    posts = Posts.query.all()
    posts2 = posts1[:8]

    # 接收用户 url传递过来的 page参数
    page = request.args.get('page', 1, type=int)
    pagination = Posts.query.order_by(Posts.timestamp.desc()).paginate(page, per_page=5, error_out=False)
    pagination2 = Posts.query.order_by(Posts.timestamp.desc()).paginate(page, per_page=8, error_out=False)
    posts3 = pagination.items
    # return render_template('main/index.html', form=form, posts=posts, pagination=pagination)

    return render_template('main/home3.html', user=u, users=users, posts=posts3, pagination=pagination)


# 发布帖子
@main.route('/publish/', methods=['GET', 'POST'])
@login_required
def publish():
    form = PostForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:  # 如果登录
            # 获取当前用户
            u = current_user._get_current_object()
            p = Posts(content=form.content.data, user=u)
            db.session.add(p)
            flash('发表成功')
            # 到时候这个跳转要修改
            return redirect(url_for('main.publish'))
        else:
            flash("请先登录")
            return redirect(url_for('users.login'))
    # 调取所有发表的博客
    # posts = Posts.query.filter_by(rid=0).all()
    # www.baidu.com?page=1
    # 接收用户 url传递过来的 page参数
    page = request.args.get('page', 1, type=int)
    pagination = Posts.query.filter_by(rid=0).order_by(Posts.timestamp.desc()).paginate(page, per_page=5,
                                                                                        error_out=False)
    posts = pagination.items
    return render_template('posts/publish.html', form=form, posts=posts, pagination=pagination)


@main.route('/more_people')
def more_people():
    users = User.query.all()
    return render_template('main/morePeople.html', users=users)


@main.route('/more_message')
def more_message():
    page = request.args.get('page', 1, type=int)
    pagination = Posts.query.order_by(Posts.timestamp.desc()).paginate(page, per_page=5, error_out=False)
    posts = pagination.items
    return render_template('main/moreMessage.html', posts=posts, pagination=pagination)


@main.route('/information')
@login_required
def information():
    # 获取当前用户
    u = current_user._get_current_object()
    # 也要获取一遍post数据和pagination数据
    page = request.args.get('page', 1, type=int)
    pagination = Posts.query.filter_by(uid=u.id).order_by(Posts.timestamp.desc()).paginate(page, per_page=5,
                                                                                           error_out=False)
    posts = pagination.items
    return render_template('user/userInfo.html', posts=posts, pagination=pagination)


@main.route('/publish_article', methods=['GET', 'POST'])
@login_required
def publish_article():
    # 发布帖子
    form = PostForm()
    if form.validate_on_submit():
        # 获取当前用户
        u = current_user._get_current_object()
        p = Posts(content=form.content.data, user=u)
        db.session.add(p)
        flash('发表成功！')
        # 获取到所有的用户自己发表的文章，然后进行显示
        # 接收用户 url传递过来的 page参数
        page = request.args.get('page', 1, type=int)
        pagination = Posts.query.filter_by(uid=u.id).order_by(Posts.timestamp.desc()).paginate(page, per_page=5,
                                                                                               error_out=False)
        posts = pagination.items
    return render_template('posts/publish.html', form=form, posts=posts, pagination=pagination)
