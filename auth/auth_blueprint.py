from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import db, User, UserInfo, AuditLog, UserService

# 创建蓝图
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['username']
        password = request.form['password']
        
        # 获取客户端信息
        ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        ua = request.headers.get('User-Agent')
        
        # 使用数据库验证用户
        user = UserService.authenticate(user_id, password, ip=ip, ua=ua)
        
        if user:
            session['user_id'] = user.id
            session['user'] = user.user_id
            session['user_type'] = user.user_type
            flash('登录成功！', 'success')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误！', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        # 记录退出日志
        ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        ua = request.headers.get('User-Agent')
        AuditLog.log_action(user_id, 'logout', ip=ip, ua=ua)
        db.session.commit()
    
    session.clear()
    flash('已退出登录！', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form['username']
        password = request.form['password']
        full_name = request.form.get('full_name', '')
        email = request.form.get('email', '')
        
        # 检查用户是否已存在
        existing_user = UserService.find_by_user_id(user_id)
        if existing_user:
            flash('用户名已存在！', 'error')
        else:
            try:
                # 判断登录类型
                login_type = 'email' if '@' in user_id else 'phone'
                
                # 创建用户
                user = UserService.create_user(
                    user_id=user_id,
                    password=password,
                    login_type=login_type,
                    user_type='passenger'
                )
                
                # 更新用户详细信息
                if full_name or email:
                    UserService.update_user_info(
                        user_id=user_id,
                        full_name=full_name,
                        email=email if email else (user_id if login_type == 'email' else None),
                        phone=user_id if login_type == 'phone' else None
                    )
                
                flash('注册成功！请登录。', 'success')
                return redirect(url_for('auth.login'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'注册失败：{str(e)}', 'error')
    
    return render_template('register.html')