# CitrusLink - 智橘云控系统

基于 FastAPI + PostgreSQL + PostGIS 的智能柑橘采摘管理系统

## 系统架构

- **后端框架**: FastAPI + SQLAlchemy ORM
- **数据库**: PostgreSQL 14 + PostGIS 扩展
- **前端**: 原生 JavaScript + Tailwind CSS
- **服务器**: Uvicorn (ASGI)

## 项目结构

```
citrus_web_backend/
├── main.py              # FastAPI 应用主文件，定义所有 API 接口
├── database_setup.py    # 数据库连接和 ORM 模型定义
├── populate_data.py     # 测试数据填充脚本
├── view_data.py         # 数据验证脚本
├── 01.html              # 前端单页应用
├── requirements.txt     # Python 依赖列表
├── setup_and_run.sh     # 一键初始化脚本
└── README.md            # 本文档
```

## 数据库表结构

系统包含 5 个核心数据表：

1. **t_sys_user** - 系统用户表
2. **t_sys_robot** - 智能终端(机器人)表
3. **t_biz_target** - 作业目标(柑橘)表（使用 PostGIS 存储地理坐标）
4. **t_biz_task** - 作业任务表
5. **t_sys_log** - 运行日志表

## 快速开始

### 方法一：使用一键脚本（推荐）

```bash
# 给脚本添加执行权限
chmod +x setup_and_run.sh

# 运行初始化脚本
./setup_and_run.sh

# 启动服务器
python3 main.py
```

### 方法二：手动安装

#### 1. 安装系统依赖

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y postgresql postgresql-contrib postgis
```

#### 2. 配置数据库

```bash
# 启动 PostgreSQL 服务
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 切换到 postgres 用户
sudo -u postgres psql

# 在 psql 中执行以下命令：
CREATE DATABASE citrus_link;
CREATE USER admin WITH PASSWORD 'citrus_pass';
GRANT ALL PRIVILEGES ON DATABASE citrus_link TO admin;
\c citrus_link
CREATE EXTENSION postgis;
\q
```

#### 3. 安装 Python 依赖

```bash
pip3 install -r requirements.txt
```

#### 4. 初始化数据库表结构

```bash
python3 database_setup.py
```

#### 5. 填充测试数据

```bash
python3 populate_data.py
```

#### 6. 验证数据

```bash
python3 view_data.py
```

#### 7. 启动服务器

```bash
python3 main.py
```

## 访问系统

启动服务器后，在浏览器中访问：

```
http://localhost:8000
```

## API 端点

系统提供以下 RESTful API：

### 1. 获取仪表盘统计数据
```
GET /api/dashboard/stats
```
返回：在线设备数、任务完成率、平均电量

### 2. 获取任务列表
```
GET /api/tasks
```
返回：所有任务的详细信息

### 3. 获取地图对象
```
GET /api/map/objects
```
返回：机器人和目标果实的位置坐标

### 4. 前端页面
```
GET /
```
返回：HTML 前端页面

## 数据库配置

如需修改数据库连接信息，请编辑 `database_setup.py` 第 9 行：

```python
DATABASE_URL = "postgresql://用户名:密码@主机:端口/数据库名"
```

默认配置：
- 主机: localhost
- 端口: 5432
- 用户名: admin
- 密码: citrus_pass
- 数据库: citrus_link

## 常见问题

### 1. 数据库连接失败

**错误**: `could not connect to server`

**解决方案**:
```bash
# 检查 PostgreSQL 是否运行
sudo systemctl status postgresql

# 如果未运行，启动服务
sudo systemctl start postgresql
```

### 2. PostGIS 扩展未找到

**错误**: `ERROR: could not open extension control file`

**解决方案**:
```bash
# Ubuntu/Debian
sudo apt install postgis postgresql-14-postgis-3

# 然后在数据库中启用扩展
sudo -u postgres psql -d citrus_link -c "CREATE EXTENSION postgis;"
```

### 3. 权限不足

**错误**: `permission denied for database`

**解决方案**:
```bash
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE citrus_link TO admin;"
sudo -u postgres psql -d citrus_link -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;"
```

### 4. 端口被占用

**错误**: `Address already in use`

**解决方案**:
```bash
# 查找占用 8000 端口的进程
sudo lsof -i :8000

# 终止进程（替换 PID）
kill -9 <PID>

# 或者在 main.py 中修改端口号
```

## 开发工具脚本

### 查看数据库内容
```bash
python3 view_data.py
```

### 重置数据库
```bash
python3 database_setup.py
python3 populate_data.py
```

## 技术栈详情

| 组件 | 版本 | 用途 |
|------|------|------|
| FastAPI | 0.109.0 | Web 框架 |
| Uvicorn | 0.27.0 | ASGI 服务器 |
| SQLAlchemy | 2.0.25 | ORM |
| GeoAlchemy2 | 0.14.3 | PostGIS 支持 |
| psycopg2-binary | 2.9.9 | PostgreSQL 驱动 |
| PostgreSQL | 14+ | 数据库 |
| PostGIS | 3.x | 地理空间扩展 |

## 系统特性

- ✅ RESTful API 设计
- ✅ SQLAlchemy ORM 管理
- ✅ PostGIS 地理坐标支持
- ✅ 实时数据更新（5秒自动刷新）
- ✅ 响应式 UI 设计
- ✅ CORS 跨域支持
- ✅ 数据库约束验证（电量 0-100%, 成熟度 0-1）

## 生产环境部署建议

1. **安全性**:
   - 修改默认数据库密码
   - 配置 CORS 白名单（在 main.py 中修改 `allow_origins`）
   - 使用 HTTPS

2. **性能优化**:
   - 使用 Gunicorn + Uvicorn workers
   - 配置数据库连接池
   - 添加 Redis 缓存

3. **监控**:
   - 配置日志记录
   - 添加性能监控工具
   - 设置数据库备份

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题，请联系开发团队。
