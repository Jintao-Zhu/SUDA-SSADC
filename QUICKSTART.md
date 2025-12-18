# CitrusLink 快速启动指南

## 📋 前置要求

- Python 3.8+
- PostgreSQL 14+
- PostGIS 扩展

## 🚀 快速启动（3 步）

### 步骤 1: 安装 Python 依赖

```bash
pip3 install -r requirements.txt
```

### 步骤 2: 配置数据库

确保 PostgreSQL 正在运行，然后执行：

```bash
# 创建数据库和用户（只需执行一次）
sudo -u postgres psql << EOF
CREATE DATABASE citrus_link;
CREATE USER admin WITH PASSWORD 'citrus_pass';
GRANT ALL PRIVILEGES ON DATABASE citrus_link TO admin;
\c citrus_link
CREATE EXTENSION postgis;
EOF
```

如果数据库已存在，可跳过此步骤。

### 步骤 3: 初始化并启动

```bash
# 测试连接
python3 test_connection.py

# 初始化数据库表
python3 database_setup.py

# 填充测试数据
python3 populate_data.py

# 启动服务器
python3 main.py
```

## 🌐 访问系统

打开浏览器访问: http://localhost:8000

## ✅ 验证安装

运行测试脚本检查环境：

```bash
python3 test_connection.py
```

## 🔧 常见问题

### 问题 1: 依赖安装失败

```bash
# 升级 pip
pip3 install --upgrade pip

# 重新安装依赖
pip3 install -r requirements.txt
```

### 问题 2: 数据库连接失败

```bash
# 检查 PostgreSQL 状态
sudo systemctl status postgresql

# 启动 PostgreSQL
sudo systemctl start postgresql
```

### 问题 3: PostGIS 扩展未安装

```bash
# Ubuntu/Debian
sudo apt install postgis postgresql-14-postgis-3

# 在数据库中启用
sudo -u postgres psql -d citrus_link -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

### 问题 4: 权限错误

```bash
# 重新授权
sudo -u postgres psql << EOF
GRANT ALL PRIVILEGES ON DATABASE citrus_link TO admin;
\c citrus_link
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin;
EOF
```

## 📊 测试数据

系统会自动创建以下测试数据：

- 1 个管理员用户 (admin)
- 1 个机器人 (UGV-01)
- 1 个目标果实 (Area-A)
- 1 个采摘任务
- 1 条系统日志

## 🔄 重置数据库

如需重新初始化数据库：

```bash
python3 database_setup.py  # 会清空并重建所有表
python3 populate_data.py   # 重新填充测试数据
```

## 📝 API 端点

- `GET /` - 前端页面
- `GET /api/dashboard/stats` - 仪表盘统计
- `GET /api/tasks` - 任务列表
- `GET /api/map/objects` - 地图对象（机器人和果实位置）

## 🎯 下一步

详细文档请查看 [README.md](README.md)
