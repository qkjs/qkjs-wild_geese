#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库表并插入初始数据
支持MySQL/MariaDB
"""

from app import create_app
from auth.models import db, User, UserInfo, UserService, AuditLog
import pymysql
import os

# 管理员凭据环境变量（任选其一）
ADMIN_USER_ENV_KEYS = [
    'MYSQL_ADMIN_USER',
    'MYSQL_ROOT_USER',
]
ADMIN_PASS_ENV_KEYS = [
    'MYSQL_ADMIN_PASSWORD',
    'MYSQL_ROOT_PASSWORD',
]


def _get_first_env(keys):
    """返回第一个存在且非空的环境变量值，否则返回 None"""
    for k in keys:
        v = os.environ.get(k)
        if v:
            return v
    return None


def ensure_database_and_grants():
    """
    确保数据库存在并为业务账号授予权限。

    行为：
    - 若提供了管理员凭据（MYSQL_ADMIN_* 或 MYSQL_ROOT_*），
      使用管理员执行：
        1) CREATE DATABASE IF NOT EXISTS <db>
        2) CREATE USER IF NOT EXISTS '<user>'@'%' IDENTIFIED BY '<password>'
        3) GRANT ALL PRIVILEGES ON <db>.* TO '<user>'@'%'
        4) FLUSH PRIVILEGES
    - 若没有管理员凭据，则尝试用业务账号直接创建数据库（要求该账号已具备 CREATE 权限）。
    """
    mysql_host = os.environ.get('MYSQL_HOST', '192.168.189.10')
    mysql_port = int(os.environ.get('MYSQL_PORT', '3306'))
    app_user = os.environ.get('MYSQL_USER', 'hy')
    app_password = os.environ.get('MYSQL_PASSWORD', 'Bosun@0428')
    mysql_database = os.environ.get('MYSQL_DATABASE', 'flask_auth_dev')

    admin_user = _get_first_env(ADMIN_USER_ENV_KEYS)
    admin_password = _get_first_env(ADMIN_PASS_ENV_KEYS)

    # 优先使用管理员凭据，进行建库与授权
    if admin_user and admin_password:
        try:
            admin_conn = pymysql.connect(
                host=mysql_host,
                port=mysql_port,
                user=admin_user,
                password=admin_password,
                charset='utf8mb4',
                connect_timeout=5,
            )
            with admin_conn.cursor() as cursor:
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{mysql_database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
                # 创建或确保业务用户存在
                cursor.execute(
                    "CREATE USER IF NOT EXISTS %s@'%' IDENTIFIED BY %s",
                    (app_user, app_password),
                )
                # 授权业务用户
                cursor.execute(
                    f"GRANT ALL PRIVILEGES ON `{mysql_database}`.* TO %s@'%'",
                    (app_user,),
                )
                cursor.execute("FLUSH PRIVILEGES")
                print(f"数据库与授权已确保：db={mysql_database}, user={app_user}@'%'")
            admin_conn.close()
            return True
        except Exception as e:
            print(f"使用管理员创建/授权失败: {e}")
            print("请检查管理员账号、网络访问控制或在服务器上执行 mysql_setup.sql")
            return False

    # 无管理员凭据，尝试用业务账号直接建库（需要已有权限）
    try:
        connection = pymysql.connect(
            host=mysql_host,
            port=mysql_port,
            user=app_user,
            password=app_password,
            charset='utf8mb4',
            connect_timeout=5,
        )
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{mysql_database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            print(f"数据库 '{mysql_database}' 已创建或已存在（使用业务账号）")
        connection.close()
        return True
    except Exception as e:
        print(f"创建数据库/授权权限不足或失败: {e}")
        print("若无管理员权限，请在服务器上执行 mysql_setup.sql，或设置 MYSQL_ADMIN_USER/MYSQL_ADMIN_PASSWORD 后重试。")
        return False


def init_database():
    """初始化数据库（建库/授权 -> 建表 -> 插入测试数据）"""
    # 确保数据库存在与权限就绪
    if not ensure_database_and_grants():
        return

    app = create_app()

    with app.app_context():
        try:
            # 删除所有表（仅用于开发环境）
            print("正在删除现有表...")
            db.drop_all()

            # 创建所有表
            print("正在创建数据库表...")
            db.create_all()

            # 创建默认用户
            print("正在创建默认用户...")

            # 管理员用户
            UserService.create_user(
                user_id='admin@example.com',
                password='password123',
                login_type='email',
                user_type='admin',
            )

            # 更新管理员详细信息
            UserService.update_user_info(
                user_id='admin@example.com',
                full_name='系统管理员',
                email='admin@example.com',
                display_name='Admin',
            )

            # 普通用户
            UserService.create_user(
                user_id='user@example.com',
                password='123456',
                login_type='email',
                user_type='passenger',
            )

            # 更新普通用户详细信息
            UserService.update_user_info(
                user_id='user@example.com',
                full_name='测试用户',
                email='user@example.com',
                display_name='TestUser',
                age=25,
                gender='male',
            )

            # 手机号用户
            phone_user = UserService.create_user(
                user_id='13800138000',
                password='123456',
                login_type='phone',
                user_type='driver',
            )

            # 更新手机号用户详细信息
            UserService.update_user_info(
                user_id='13800138000',
                full_name='司机用户',
                phone='13800138000',
                display_name='Driver01',
                age=30,
                gender='male',
            )

            # 设置司机扩展资料
            if phone_user.user_info:
                phone_user.user_info.set_extra_profile('license_number', 'DL123456789')
                phone_user.user_info.set_extra_profile('vehicle_type', 'sedan')
                db.session.commit()

            print("MySQL数据库初始化完成！")
            print(f"\n数据库连接信息:")
            print(f"主机: {app.config.get('MYSQL_HOST', 'localhost')}")
            print(f"端口: {app.config.get('MYSQL_PORT', '3306')}")
            print(f"数据库: {app.config.get('MYSQL_DATABASE', 'flask_auth_dev')}")
            print("\n默认用户账号:")
            print("1. 管理员: admin@example.com / password123")
            print("2. 普通用户: user@example.com / 123456")
            print("3. 司机用户: 13800138000 / 123456")

        except Exception as e:
            print(f"初始化数据库时出错: {e}")
            print("请检查MySQL连接配置和权限")


def show_users():
    """显示所有用户"""
    app = create_app()

    with app.app_context():
        users = User.query.all()
        print(f"\n共有 {len(users)} 个用户:")
        print("-" * 80)

        for user in users:
            print(f"ID: {user.id}")
            print(f"用户名: {user.user_id}")
            print(f"登录类型: {user.login_type}")
            print(f"用户类型: {user.user_type}")
            print(f"状态: {user.status}")
            print(f"创建时间: {user.created_at}")

            if user.user_info:
                print(f"姓名: {user.user_info.full_name}")
                print(f"昵称: {user.user_info.display_name}")
                print(f"邮箱: {user.user_info.email}")
                print(f"手机: {user.user_info.phone}")
                if user.user_info.extra_profile:
                    print(f"扩展资料: {user.user_info.extra_profile}")

            print("-" * 80)


def show_audit_logs():
    """显示审计日志"""
    app = create_app()

    with app.app_context():
        logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(20).all()
        print(f"\n最近 {len(logs)} 条审计日志:")
        print("-" * 80)

        for log in logs:
            print(f"时间: {log.created_at}")
            print(f"用户ID: {log.actor_user_id}")
            print(f"动作: {log.action}")
            print(f"目标: {log.target}")
            print(f"IP: {log.ip}")
            print("-" * 40)


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'init':
            init_database()
        elif command == 'users':
            show_users()
        elif command == 'logs':
            show_audit_logs()
        else:
            print("使用方法:")
            print("  python init_db.py init    - 初始化数据库")
            print("  python init_db.py users   - 显示所有用户")
            print("  python init_db.py logs    - 显示审计日志")
    else:
        init_database()
    
        
def show_users():
    """显示所有用户"""
    app = create_app()
    
    with app.app_context():
        users = User.query.all()
        print(f"\n共有 {len(users)} 个用户:")
        print("-" * 80)
        
        for user in users:
            print(f"ID: {user.id}")
            print(f"用户名: {user.user_id}")
            print(f"登录类型: {user.login_type}")
            print(f"用户类型: {user.user_type}")
            print(f"状态: {user.status}")
            print(f"创建时间: {user.created_at}")
            
            if user.user_info:
                print(f"姓名: {user.user_info.full_name}")
                print(f"昵称: {user.user_info.display_name}")
                print(f"邮箱: {user.user_info.email}")
                print(f"手机: {user.user_info.phone}")
                if user.user_info.extra_profile:
                    print(f"扩展资料: {user.user_info.extra_profile}")
            
            print("-" * 80)

def show_audit_logs():
    """显示审计日志"""
    app = create_app()
    
    with app.app_context():
        logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(20).all()
        print(f"\n最近 {len(logs)} 条审计日志:")
        print("-" * 80)
        
        for log in logs:
            print(f"时间: {log.created_at}")
            print(f"用户ID: {log.actor_user_id}")
            print(f"动作: {log.action}")
            print(f"目标: {log.target}")
            print(f"IP: {log.ip}")
            print("-" * 40)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'init':
            init_database()
        elif command == 'users':
            show_users()
        elif command == 'logs':
            show_audit_logs()
        else:
            print("使用方法:")
            print("  python init_db.py init    - 初始化数据库")
            print("  python init_db.py users   - 显示所有用户")
            print("  python init_db.py logs    - 显示审计日志")
    else:
        init_database()