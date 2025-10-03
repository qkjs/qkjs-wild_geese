-- MariaDB 数据库和用户创建脚本
-- 请在MariaDB命令行或phpMyAdmin中执行
-- 注意：此脚本配置为允许从 192.168.189.0/24 网段访问

-- 创建数据库
CREATE DATABASE IF NOT EXISTS flask_auth_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS flask_auth CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 如果用户hy不存在，则创建用户（请根据实际情况调整）
-- CREATE USER IF NOT EXISTS 'hy'@'localhost' IDENTIFIED BY 'Bosun@0428';
-- CREATE USER IF NOT EXISTS 'hy'@'192.168.189.%' IDENTIFIED BY 'Bosun@0428';

-- 为用户hy授权访问数据库（本地访问）
GRANT ALL PRIVILEGES ON flask_auth_dev.* TO 'hy'@'localhost';
GRANT ALL PRIVILEGES ON flask_auth.* TO 'hy'@'localhost';

-- 为用户hy授权访问数据库（任意来源，或可按需收紧为具体网段）
GRANT ALL PRIVILEGES ON flask_auth_dev.* TO 'hy'@'%';
GRANT ALL PRIVILEGES ON flask_auth.* TO 'hy'@'%';

-- 刷新权限
FLUSH PRIVILEGES;

-- 显示创建的数据库
SHOW DATABASES LIKE 'flask_auth%';

-- 显示用户权限
SHOW GRANTS FOR 'hy'@'localhost';
SHOW GRANTS FOR 'hy'@'192.168.189.%';