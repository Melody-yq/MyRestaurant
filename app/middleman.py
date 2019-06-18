#作为中间人的角色
from flask import Flask,render_template,redirect,url_for
from app.config import config
import app.__init__ as init

#创建实例并完成实例和对象的绑定
pp =init.create_app('development')
pp.route('/')
def index():
    render_template('common/home.html')


