from flask import Flask
from auth.auth_blueprint import auth_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your-secret-key-change-this-in-production'
    
    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    @app.route('/')
    def index():
        return '<h1>Welcome!</h1><a href="/auth/login">Login</a>'
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)