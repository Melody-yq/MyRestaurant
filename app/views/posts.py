from flask import Blueprint,render_template,url_for,request,flash,get_flashed_messages,redirect,jsonify

posts = Blueprint('posts',__name__)


@posts.route('/collect/<pid>/')
def collect(pid):
    return jsonify({'result':'ok'})