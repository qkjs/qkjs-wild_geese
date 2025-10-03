from flask import Flask
from auth import auth_bp, db
from config import config
import os
from main import main_bp

def create_app(config_name=None):
    app = Flask(__name__)
    
    # 选择配置
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # 初始化数据库
    db.init_app(app)
    
    # 注册蓝图
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    return app

if __name__ == '__main__':
    app = create_app()
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', '5000'))
    debug = app.config.get('DEBUG', True)
    app.run(host=host, port=port, debug=debug)