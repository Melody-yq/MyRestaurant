from flask import Flask, render_template
from app.config import config
from app.exts import config_extensions
from app.views import config_blueprint


# 封装一个函数  专门用来创建实例
def create_app(config_name):
    # 创建实例
    app = Flask(__name__)
    # 初始化配置
    app.config.from_object(config[config_name])
    # #调用初始化方法
    config[config_name].init_app(app)
    # 错误页面显示
    config_errorhandler(app)
    # 调用扩展方法 完成 app跟扩展对象的绑定
    config_extensions(app)
    # 完成蓝本的注册
    config_blueprint(app)
    return app


def config_errorhandler(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error/404.html')
