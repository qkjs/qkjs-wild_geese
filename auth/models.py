from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(db.Model):
    """用户基础信息表"""
    __tablename__ = 'users'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(255), unique=True, nullable=False, index=True)  # 登录账号
    login_type = db.Column(db.String(16), nullable=False, default='email')  # email/phone
    password_hash = db.Column(db.Text, nullable=False)
    mfa_secret_enc = db.Column(db.Text, nullable=True)  # MFA 秘钥
    user_type = db.Column(db.String(16), nullable=False, default='passenger')  # passenger/driver/admin/cs
    status = db.Column(db.String(16), nullable=False, default='active')  # active/disabled/pending
    pwd_changed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # MySQL特定配置
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }
    
    # 与用户详细信息的一对一关系
    user_info = db.relationship('UserInfo', backref='user', uselist=False, cascade='all, delete-orphan')
    
    # 与审计日志的一对多关系
    audit_logs = db.relationship('AuditLog', backref='actor_user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
        self.pwd_changed_at = datetime.utcnow()
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def is_active(self):
        """检查用户是否激活"""
        return self.status == 'active'
    
    def is_admin(self):
        """检查是否为管理员"""
        return self.user_type == 'admin'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'login_type': self.login_type,
            'user_type': self.user_type,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.user_id}>'


class UserInfo(db.Model):
    """用户详细信息表"""
    __tablename__ = 'users_info'
    
    id = db.Column(db.BigInteger, db.ForeignKey('users.id'), primary_key=True)
    full_name = db.Column(db.String(128), nullable=True)
    phone = db.Column(db.String(32), nullable=True)  # E.164 格式
    email = db.Column(db.String(255), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(16), nullable=True)
    display_name = db.Column(db.String(128), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    extra_profile = db.Column(db.JSON, nullable=True)  # 扩展资料
    
    # MySQL特定配置
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }
    
    def set_extra_profile(self, key, value):
        """设置扩展资料"""
        if self.extra_profile is None:
            self.extra_profile = {}
        self.extra_profile[key] = value
        # 标记字段已修改
        db.session.merge(self)
    
    def get_extra_profile(self, key, default=None):
        """获取扩展资料"""
        if self.extra_profile is None:
            return default
        return self.extra_profile.get(key, default)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'phone': self.phone,
            'email': self.email,
            'age': self.age,
            'gender': self.gender,
            'display_name': self.display_name,
            'address': self.address,
            'extra_profile': self.extra_profile
        }
    
    def __repr__(self):
        return f'<UserInfo {self.full_name or self.display_name}>'


class AuditLog(db.Model):
    """审计日志表"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    actor_user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(64), nullable=False)  # login_success/login_failed等
    target = db.Column(db.String(64), nullable=True)  # 作用对象
    ip = db.Column(db.String(64), nullable=True)  # IP地址
    ua = db.Column(db.Text, nullable=True)  # User-Agent
    context = db.Column(db.JSON, nullable=True)  # 上下文信息
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # MySQL特定配置
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }
    
    @staticmethod
    def log_action(user_id, action, target=None, ip=None, ua=None, context=None):
        """记录审计日志"""
        log = AuditLog(
            actor_user_id=user_id,
            action=action,
            target=target,
            ip=ip,
            ua=ua,
            context=context
        )
        db.session.add(log)
        return log
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'actor_user_id': self.actor_user_id,
            'action': self.action,
            'target': self.target,
            'ip': self.ip,
            'ua': self.ua,
            'context': self.context,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<AuditLog {self.action} by user {self.actor_user_id}>'


# 便捷的查询方法
class UserService:
    """用户服务类，提供常用的用户操作方法"""
    
    @staticmethod
    def create_user(user_id, password, login_type='email', user_type='passenger', **kwargs):
        """创建用户"""
        user = User(
            user_id=user_id,
            login_type=login_type,
            user_type=user_type,
            **kwargs
        )
        user.set_password(password)
        
        # 创建用户详细信息
        user_info = UserInfo(id=user.id)
        user.user_info = user_info
        
        db.session.add(user)
        db.session.commit()
        
        # 记录创建日志
        AuditLog.log_action(user.id, 'user_created')
        db.session.commit()
        
        return user
    
    @staticmethod
    def find_by_user_id(user_id):
        """根据登录账号查找用户"""
        return User.query.filter_by(user_id=user_id).first()
    
    @staticmethod
    def find_by_id(id):
        """根据ID查找用户"""
        return User.query.get(id)
    
    @staticmethod
    def authenticate(user_id, password, ip=None, ua=None):
        """用户认证"""
        user = UserService.find_by_user_id(user_id)
        
        if user and user.check_password(password) and user.is_active():
            # 记录登录成功
            AuditLog.log_action(user.id, 'login_success', ip=ip, ua=ua)
            db.session.commit()
            return user
        else:
            # 记录登录失败
            if user:
                AuditLog.log_action(user.id, 'login_failed', ip=ip, ua=ua)
            db.session.commit()
            return None
    
    @staticmethod
    def update_user_info(user_id, **kwargs):
        """更新用户信息"""
        user = UserService.find_by_user_id(user_id)
        if not user:
            return None
        
        if not user.user_info:
            user.user_info = UserInfo(id=user.id)
        
        for key, value in kwargs.items():
            if hasattr(user.user_info, key):
                setattr(user.user_info, key, value)
        
        db.session.commit()
        return user