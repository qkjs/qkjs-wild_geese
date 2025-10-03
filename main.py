from flask import Blueprint, render_template, session, redirect, url_for, flash
from auth import UserService

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/detail')
def detail():
    """用户详情页：需要登录，显示基础与扩展信息"""
    user_id = session.get('user_id')
    if not user_id:
        flash('请先登录再查看详情', 'info')
        return redirect(url_for('auth.page_login'))

    user = UserService.find_by_user_id(user_id)
    user_info = user.user_info if user else None
    return render_template('detail.html', user=user, user_info=user_info)
