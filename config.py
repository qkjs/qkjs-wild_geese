"""
数据库配置文件
"""
import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL

# 加载 .env 文件
load_dotenv()

class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0
    }

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    
    # MariaDB 开发环境配置
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or '192.168.189.10'
    MYSQL_PORT = os.environ.get('MYSQL_PORT') or '3306'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'hy'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'Bosun@0428'
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'flask_auth_dev'
    
    # 使用 URL.create 安全构造连接串，避免密码中的特殊字符（如 @）破坏解析
    SQLALCHEMY_DATABASE_URI = URL.create(
        drivername='mysql+pymysql',
        username=MYSQL_USER,
        password=MYSQL_PASSWORD,
        host=MYSQL_HOST,
        port=int(MYSQL_PORT),
        database=MYSQL_DATABASE,
        query={'charset': 'utf8mb4'}
    )

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    
    # MariaDB 生产环境配置
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or '192.168.189.10'
    MYSQL_PORT = os.environ.get('MYSQL_PORT') or '3306'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'hy'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'Bosun@0428'
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'flask_auth'
    
    SQLALCHEMY_DATABASE_URI = URL.create(
        drivername='mysql+pymysql',
        username=MYSQL_USER,
        password=MYSQL_PASSWORD,
        host=MYSQL_HOST,
        port=int(MYSQL_PORT),
        database=MYSQL_DATABASE,
        query={'charset': 'utf8mb4'}
    )

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    
    # 测试用SQLite内存数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}