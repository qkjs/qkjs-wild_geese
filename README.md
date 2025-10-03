# Flask 登录蓝图项目（MariaDB版）

这是一个基于 Flask 的用户认证系统，使用蓝图（Blueprint）架构和 MariaDB 数据库。

## 项目结构

```
qkjs-wild_geese/
├── app.py                    # 主应用文件
├── config.py                 # 配置文件
├── init_db.py               # 数据库初始化脚本
├── mysql_setup.sql          # MariaDB数据库设置脚本
├── .env.example             # 环境变量配置示例
├── .env                     # 环境变量配置（本地）
├── .gitignore              # Git忽略文件
├── auth/
│   ├── __init__.py          # 认证模块初始化
│   ├── models.py            # 用户认证相关模型
│   └── auth_blueprint.py    # 认证蓝图
├── templates/
│   ├── index.html           # 首页模板
│   ├── login.html           # 登录页面模板
│   └── register.html        # 注册页面模板
├── requirements.txt         # 依赖文件
└── README.md               # 说明文档
```

## 数据库设计

使用 MariaDB 数据库，基于提供的数据库设计文档，包含以下表：

## 模块化架构

项目采用模块化设计：

### auth 模块
- `auth/models.py` - 用户认证相关的数据模型
  - `User` - 用户基础信息模型
  - `UserInfo` - 用户详细信息模型  
  - `AuditLog` - 审计日志模型
  - `UserService` - 用户服务类
- `auth/auth_blueprint.py` - 认证相关的路由和视图
- `auth/__init__.py` - 模块初始化，统一导出接口

### 核心文件
- `app.py` - Flask应用工厂
- `config.py` - 应用配置管理
- `init_db.py` - 数据库初始化工具

### users 表（用户基础信息）
- `id` - 主键，自增
- `user_id` - 登录账号（邮箱或手机号）
- `login_type` - 账号类型：email/phone
- `password_hash` - 密码哈希
- `user_type` - 用户类型：passenger/driver/admin/cs
- `status` - 账号状态：active/disabled/pending
- `pwd_changed_at` - 上次密码修改时间
- `created_at/updated_at` - 创建/更新时间

### users_info 表（用户详细信息）
- `id` - 外键，关联users.id
- `full_name` - 姓名
- `phone` - 手机号（E.164格式）
- `email` - 资料邮箱
- `age` - 年龄
- `gender` - 性别
- `display_name` - 昵称
- `address` - 地址
- `extra_profile` - 扩展资料（JSON格式）

### audit_logs 表（审计日志）
- `id` - 主键，自增
- `actor_user_id` - 操作者用户ID
- `action` - 动作（如login_success/login_failed）
- `target` - 作用对象
- `ip` - IP地址
- `ua` - User-Agent
- `context` - 上下文（JSON格式）
- `created_at` - 日志时间

## 功能特性

- ✅ 用户注册与登录
- ✅ 密码安全哈希存储
- ✅ 会话管理
- ✅ 审计日志记录
- ✅ 支持邮箱和手机号登录
- ✅ 用户类型管理（乘客/司机/管理员/客服）
- ✅ 用户详细信息管理
- ✅ JSON扩展字段支持
- ✅ Flash 消息提示
- ✅ 响应式UI界面

## 安装和运行

### 1. 环境准备

确保已安装：
- Python 3.7+
- MariaDB 10.3+ 或更高版本

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. MariaDB 数据库设置

#### 方法一：使用提供的SQL脚本
```bash
mariadb -u hy -p -h 192.168.189.10 < mysql_setup.sql
```

#### 方法二：手动创建
```sql
CREATE DATABASE flask_auth_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON flask_auth_dev.* TO 'hy'@'192.168.189.%';
FLUSH PRIVILEGES;
```

#### 重要网络配置
确保MariaDB服务器 (192.168.189.10) 的配置：
1. 绑定地址允许外部连接：`bind-address = 0.0.0.0`
2. 防火墙开放3306端口
3. 用户权限允许远程访问

### 4. 环境变量配置

复制配置文件并修改：
```bash
cp .env.example .env
```

编辑 `.env` 文件，设置您的MariaDB连接信息：
```env
MYSQL_HOST=192.168.189.10
MYSQL_PORT=3306
MYSQL_USER=hy
MYSQL_PASSWORD=Bosun@0428
MYSQL_DATABASE=flask_auth_dev
```

### 5. 测试数据库连接

在初始化之前，可以先测试连接：
```bash
python -c "
import pymysql
try:
    conn = pymysql.connect(host='192.168.189.10', user='hy', password='Bosun@0428', charset='utf8mb4')
    print('✅ MariaDB连接成功！')
    conn.close()
except Exception as e:
    print(f'❌ 连接失败: {e}')
"
```

### 6. 初始化数据库

```bash
python init_db.py init
```

可选：如果当前业务账号没有建库/授权权限，可以提供管理员凭据（仅用于初始化时自动授权），在 `.env` 中设置：

```env
# 任意一种即可
MYSQL_ADMIN_USER=root
MYSQL_ADMIN_PASSWORD=your-root-password
# 或者
MYSQL_ROOT_USER=root
MYSQL_ROOT_PASSWORD=your-root-password
```

再次执行：

```bash
python init_db.py init
```

### 7. 运行应用

```bash
python app.py
```

### 8. 访问应用

打开浏览器访问 `http://127.0.0.1:5000`

## 配置说明

### 环境变量

项目支持通过环境变量配置：

- `FLASK_ENV`: Flask环境 (development/production/testing)
- `SECRET_KEY`: Flask应用密钥
- `MYSQL_HOST`: MariaDB服务器地址（默认: 192.168.189.10）
- `MYSQL_PORT`: MariaDB端口（默认3306）
- `MYSQL_USER`: MariaDB用户名（默认: hy）
- `MYSQL_PASSWORD`: MariaDB密码（默认: Bosun@0428）
- `MYSQL_DATABASE`: 数据库名称

### 配置文件

`config.py` 包含不同环境的配置：
- `DevelopmentConfig`: 开发环境
- `ProductionConfig`: 生产环境
- `TestingConfig`: 测试环境

## MariaDB 特性

### 数据库特性
- ✅ UTF8MB4 字符集，支持emoji和多语言
- ✅ InnoDB存储引擎，支持事务
- ✅ JSON字段类型，存储扩展数据
- ✅ 外键约束，数据完整性
- ✅ 连接池管理，提高性能
- ✅ 与MySQL高度兼容

### 性能优化
- 连接池预检测 (pool_pre_ping)
- 连接回收机制 (pool_recycle: 300秒)
- 连接超时设置 (pool_timeout: 20秒)

## 默认用户

系统初始化后会创建以下测试用户：

1. **管理员用户**
   - 用户名: `admin@example.com`
   - 密码: `password123`
   - 类型: admin

2. **普通用户**
   - 用户名: `user@example.com`
   - 密码: `123456`
   - 类型: passenger

3. **司机用户**
   - 用户名: `13800138000`
   - 密码: `123456`
   - 类型: driver

## API 说明

### UserService 类

提供便捷的用户操作方法：

- `create_user()` - 创建用户
- `find_by_user_id()` - 根据登录账号查找用户
- `authenticate()` - 用户认证
- `update_user_info()` - 更新用户信息

### 模型方法

- `User.set_password()` - 设置密码
- `User.check_password()` - 验证密码
- `UserInfo.set_extra_profile()` - 设置扩展资料
- `AuditLog.log_action()` - 记录审计日志

## 路由说明

- `/` - 首页
- `/auth/login` - 登录页面
- `/auth/register` - 注册页面
- `/auth/logout` - 退出登录

## 安全特性

- ✅ 密码使用 Werkzeug 安全哈希
- ✅ 登录/登出/注册操作记录审计日志
- ✅ IP地址和User-Agent追踪
- ✅ 用户状态管理
- ✅ 会话安全

## 数据库管理

### 初始化数据库
```bash
python init_db.py init
```

### 查看所有用户
```bash
python init_db.py users
```

### 查看审计日志
```bash
python init_db.py logs
```

## 故障排除

### 常见问题

1. **连接MariaDB失败**
   ```
   pymysql.err.OperationalError: (2003, "Can't connect to MariaDB server")
   ```
   - 检查MariaDB服务是否启动：`systemctl status mariadb`
   - 确认服务器地址可达：`ping 192.168.189.10`
   - 检查端口是否开放：`telnet 192.168.189.10 3306`
   - 确认防火墙设置允许3306端口

2. **网络连接超时**
   ```
   pymysql.err.OperationalError: (2003, "Can't connect to MariaDB server on '192.168.189.10'")
   ```
   - 检查网络连通性
   - 确认MariaDB绑定地址配置：`bind-address = 0.0.0.0`
   - 检查MariaDB配置文件 `/etc/mysql/mariadb.conf.d/50-server.cnf`

2. **数据库不存在**
   ```
   pymysql.err.OperationalError: (1049, "Unknown database")
   ```
   - 运行 `mysql_setup.sql` 创建数据库
   - 或手动创建数据库

3. **权限不足**
   ```
   pymysql.err.OperationalError: (1045, "Access denied for user")
   ```
   - 检查MariaDB用户权限
   - 确认用户名和密码正确
   - 运行 `SHOW GRANTS FOR 'hy'@'%';` 查看权限
   - 确保用户允许从客户端IP访问
   - 可在服务器上执行 `mysql_setup.sql` 以授予所需权限

4. **字符集问题**
   - 确保数据库使用 `utf8mb4` 字符集
   - 检查MariaDB配置文件中的字符集设置

## 扩展建议

- 添加密码复杂度验证
- 实现邮箱验证功能
- 添加手机短信验证
- 实现MFA双因素认证
- 添加密码重置功能
- 实现用户权限系统
- 添加API接口文档
- 集成Redis做会话存储
- 添加数据库备份和恢复功能
- 实现读写分离和主从复制