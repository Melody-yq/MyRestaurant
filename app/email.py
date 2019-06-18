from app.exts import mail
from flask_mail import Message
from flask import current_app, render_template
from threading import Thread


# 异步发送邮件
def send_mail(to, subject, template, **kwargs):
    # 获取当前的app实例  跨页面获取 需要 current_app
    app = current_app._get_current_object()
    msg = Message(subject=subject, recipients=[to], sender=app.config['MAIL_USERNAME'])
    # 浏览器查看邮件内容
    msg.html = render_template(template + '.html', **kwargs)
    # 终端查看邮件内容
    msg.body = render_template(template + '.txt', **kwargs)
    # 创建线程
    thr = Thread(target=async_send_mail, args=[app, msg])
    thr.start()
    return thr


def async_send_mail(app, msg):
    with app.app_context():
        mail.send(message=msg)
