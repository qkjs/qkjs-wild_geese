# Flask 登录蓝图项目

这是一个基于 Flask 的最小化登录系统，使用蓝图（Blueprint）架构。

## 项目结构

```
qkjs-wild_geese/
├── app.py                    # 主应用文件
├── auth/
│   └── auth_blueprint.py     # 认证蓝图
├── templates/
│   ├── login.html           # 登录页面模板
│   └── register.html        # 注册页面模板
└── README.md               # 说明文档
```

## 功能特性

- 用户登录
- 用户注册
- 会话管理
- Flash 消息提示
- 简洁的 UI 界面

## 安装和运行

1. 安装 Flask：
```bash
pip install flask
```

2. 运行应用：
```bash
python app.py
```

3. 访问应用：
打开浏览器访问 `http://127.0.0.1:5000`

## 默认用户

系统预设了两个测试用户：
- 用户名: `admin`, 密码: `password123`
- 用户名: `user`, 密码: `123456`

## 路由说明

- `/` - 首页
- `/auth/login` - 登录页面
- `/auth/register` - 注册页面
- `/auth/logout` - 退出登录

## 注意事项

⚠️ **重要**: 这是一个最小化的演示项目，不适合直接用于生产环境。在实际项目中请考虑：

1. 使用数据库存储用户信息
2. 密码加密（bcrypt）
3. 更强的密钥管理
4. 表单验证
5. CSRF 保护
6. 更完善的错误处理

## 扩展建议

- 集成 SQLAlchemy 进行数据库操作
- 使用 Flask-Login 进行用户会话管理
- 添加 Flask-WTF 进行表单验证
- 使用 Flask-Bcrypt 进行密码加密