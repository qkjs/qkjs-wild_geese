from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from .models import db, User, UserInfo, AuditLog, UserService

# 创建蓝图（指定本蓝图的模板目录）
auth_bp = Blueprint('auth', __name__, template_folder='templates')

# page
@auth_bp.route('/login', methods=['GET'])
def page_login():
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def page_register():
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
                return redirect(url_for('auth.page_login'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'注册失败：{str(e)}', 'error')
    
    return render_template('register.html')

# API
@auth_bp.route('/api/v1/login', methods=['POST'])
def api_login():
    # 仅接受 JSON 请求体
    data = request.get_json(silent=True) or {}
    user_id = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not user_id or not password:
        return jsonify({
            'ok': False,
            'error': 'missing_credentials',
            'detail': '用户名或密码不能为空'
        }), 400

    ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
    ua = request.headers.get('User-Agent')

    user = UserService.authenticate(user_id, password, ip=ip, ua=ua)
    if user:
        # 设置会话
        session['user_id'] = user.user_id
        session['user_type'] = user.user_type
        return jsonify({
            'ok': True,
            'redirect': url_for('index')
        })
    else:
        return jsonify({
            'ok': False,
            'error': 'invalid_credentials',
            'detail': '用户名或密码错误'
        }), 401

@auth_bp.route('/api/v1/logout', methods=['POST'])
def api_logout():
    user_login = session.get('user_id')
    if user_login:
        # 记录退出日志（需要将登录名转换为用户数值ID）
        ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        ua = request.headers.get('User-Agent')
        from .models import UserService
        user = UserService.find_by_user_id(user_login)
        if user:
            AuditLog.log_action(user.id, 'logout', ip=ip, ua=ua)
            db.session.commit()
        else:
            db.session.rollback()
    
    session.clear()
    flash('已退出登录！', 'info')
    return redirect(url_for('index'))

# 移除重复的 /register 路由（已合并到 page_register）