from .main import main
from .users import users
from .posts import posts
#蓝本配置
DEFAULT_BLUEPRINT = (
    (main,''),
    (users,'/users'),
    (posts,'/posts')
)
#以上是批量注册

#封装函数 完成蓝本注册
def config_blueprint(app):
    for blueprint,url_prefix in DEFAULT_BLUEPRINT:
        app.register_blueprint(blueprint,url_prefix=url_prefix)