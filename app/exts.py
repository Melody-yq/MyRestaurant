from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_moment import Moment
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class
from flask_migrate import Migrate, MigrateCommand
from flask_login import LoginManager

# 创建对象
bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()
migrate = Migrate(db=db)
moment = Moment()
photos = UploadSet('photos', IMAGES)
login_manager = LoginManager()


# 完成对象 跟 实例的绑定

def config_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app)
    moment.init_app(app)

    configure_uploads(app, photos)
    patch_request_class(app, size=None)
    # -----------------登录相关设置---------------------
    login_manager.init_app(app)
    # 设置登录提示消息
    login_manager.login_message = "需要登录才可以访问"
    # 设置登录的站点
    login_manager.login_view = 'users.login'
    # session 保护级别  none 不保护  basic 基本保护 strong 强保护
    login_manager.session_protection = 'strong'
