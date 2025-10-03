from flask import Blueprint, render_template, request, redirect, url_for, flash, session

# 创建蓝图
auth_bp = Blueprint('auth', __name__)

# 简单的用户数据（实际项目中应该使用数据库）
users = {
    'admin': 'password123',
    'user': '123456'
}

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 验证用户
        if username in users and users[username] == password:
            session['user'] = username
            flash('登录成功！', 'success')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误！', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash('已退出登录！', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users:
            flash('用户名已存在！', 'error')
        else:
            users[username] = password
            flash('注册成功！请登录。', 'success')
            return redirect(url_for('auth.login'))
    
    return render_template('register.html')